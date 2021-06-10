import asyncio
import functools
import logging
import multiprocessing
import os
import re
import sys
import queue
import typing
import uuid

import mitmproxy.certs
import mitmproxy.ctx
import mitmproxy.log
import mitmproxy.master
import mitmproxy.options
import mitmproxy.proxy
from mitmproxy.addons import core, clientplayback
from mitmproxy.http import HTTPFlow
import OpenSSL

from hippolyzer.lib.base.helpers import get_resource_filename
from hippolyzer.lib.base.multiprocessing_utils import ParentProcessWatcher

orig_sethostflags = OpenSSL.SSL._lib.X509_VERIFY_PARAM_set_hostflags  # noqa


@functools.wraps(orig_sethostflags)
def _sethostflags_wrapper(param, flags):
    # Since 2000 the recommendation per RFCs has been to only check SANs and not the CN field.
    # Most browsers do this, as does mitmproxy. The viewer does not, and the sim certs have no SAN
    # field. Just monkeypatch out this flag since mitmproxy's internals are in flux and there's
    # no good way to stop setting this flag currently.
    return orig_sethostflags(
        param,
        flags & (~OpenSSL.SSL._lib.X509_CHECK_FLAG_NEVER_CHECK_SUBJECT)  # noqa
    )


OpenSSL.SSL._lib.X509_VERIFY_PARAM_set_hostflags = _sethostflags_wrapper  # noqa


class SLCertStore(mitmproxy.certs.CertStore):
    def get_cert(self, commonname: typing.Optional[bytes], sans: typing.List[bytes], *args):
        cert, privkey, chain = super().get_cert(commonname, sans, *args)
        x509: OpenSSL.crypto.X509 = cert.x509
        for i in range(0, x509.get_extension_count()):
            ext = x509.get_extension(i)
            # This cert already has a subject key id, pass through.
            if ext.get_short_name() == b"subjectKeyIdentifier":
                return cert, privkey, chain

        # Need to add a subject key ID onto this cert or the viewer will reject it.
        x509.add_extensions([
            OpenSSL.crypto.X509Extension(
                b"subjectKeyIdentifier",
                False,
                uuid.uuid4().hex.encode("utf8"),
            ),
        ])
        x509.sign(privkey, "sha256")  # type: ignore
        return cert, privkey, chain


class SLProxyConfig(mitmproxy.proxy.ProxyConfig):
    def configure(self, options, updated) -> None:
        super().configure(options, updated)
        old_cert_store = self.certstore
        # Replace the cert store with one that knows how to add
        # a subject key ID extension.
        self.certstore = SLCertStore(  # noqa
            default_privatekey=old_cert_store.default_privatekey,
            default_ca=old_cert_store.default_ca,
            default_chain_file=old_cert_store.default_chain_file,
            dhparams=old_cert_store.dhparams,
        )
        self.certstore.certs = old_cert_store.certs


class HTTPFlowContext:
    def __init__(self):
        self.from_proxy_queue = multiprocessing.Queue()
        self.to_proxy_queue = multiprocessing.Queue()
        self.shutdown_signal = multiprocessing.Event()
        self.mitmproxy_ready = multiprocessing.Event()


class IPCInterceptionAddon:
    """
    Intercepts flows from mitmproxy during the request and response handling phase,
    handing them off to the main process. The main process sends back a modified
    flow which is merged in and resumed.
    """
    def __init__(self, flow_context: HTTPFlowContext):
        self.intercepted_flows: typing.Dict[str, HTTPFlow] = {}
        self.from_proxy_queue: multiprocessing.Queue = flow_context.from_proxy_queue
        self.to_proxy_queue: multiprocessing.Queue = flow_context.to_proxy_queue
        self.shutdown_signal: multiprocessing.Event = flow_context.shutdown_signal

    def log(self, entry: mitmproxy.log.LogEntry):
        if entry.level == "debug":
            logging.debug(entry.msg)
        elif entry.level in ("alert", "info"):
            # TODO: All mitmproxy infos are basically debugs, should
            #  probably give these dedicated loggers
            logging.debug(entry.msg)
        elif entry.level == "warn":
            logging.warning(entry.msg)
        elif entry.level == "error":
            logging.error(entry.msg)

    def running(self):
        # register to pump the events or something here
        asyncio.create_task(self._pump_callbacks())

    async def _pump_callbacks(self):
        watcher = ParentProcessWatcher(self.shutdown_signal)

        while not watcher.check_shutdown_needed():
            orig_flow: typing.Optional[HTTPFlow] = None
            try:
                try:
                    event_type, flow_id, flow_state = self.to_proxy_queue.get(False)
                except queue.Empty:
                    await asyncio.sleep(0.001)
                    continue
                if event_type == "callback":
                    orig_flow = self.intercepted_flows.pop(flow_id)
                    orig_flow.set_state(flow_state)
                    # Remove the taken flag from the flow if present, the flow by definition
                    # isn't take()n anymore once it's been passed back to the proxy.
                    orig_flow.metadata.pop("taken", None)
                elif event_type == "replay":
                    flow: HTTPFlow = HTTPFlow.from_state(flow_state)
                    # mitmproxy won't replay intercepted flows, this is an old flow so
                    # it's ok to unmark it.
                    flow.intercepted = False
                    mitmproxy.ctx.master.commands.call(
                        "replay.client", [flow])
                else:
                    raise ValueError(f"Unknown event type {event_type}")
            except:
                logging.exception("Failed in HTTP callback")
            finally:
                if orig_flow is not None:
                    orig_flow.resume()
        mitmproxy.ctx.master.shutdown()

    def request(self, flow: HTTPFlow):
        # This should only appear in the UA of the integrated browser
        from_browser = "Mozilla" in flow.request.headers.get("User-Agent", "")
        flow.metadata["from_browser"] = from_browser
        # Only trust the "injected" header if not from a browser
        was_injected = flow.request.headers.pop("X-Hippo-Injected", False)
        if was_injected and not from_browser:
            flow.metadata["request_injected"] = True

        # Does this request need the stupid hack around aiohttp's windows proactor bug
        need_ssl_hack = flow.request.headers.pop("X-Hippo-Windows-SSL-Hack", None) == "1"
        if need_ssl_hack and sys.platform == "win32":
            flow.request.url = re.sub(r"^http:", "https:", flow.request.url)
        self._queue_flow_interception("request", flow)

    def _queue_flow_interception(self, event_type: str, flow: HTTPFlow):
        flow.intercept()
        self.intercepted_flows[flow.id] = flow
        self.from_proxy_queue.put((event_type, flow.get_state()), True)

    def responseheaders(self, flow: HTTPFlow):
        # The response was injected earlier in an earlier handler,
        # we don't want to touch this anymore.
        if flow.metadata["response_injected"]:
            return

        # Someone fucked up and put a mimetype in Content-Encoding.
        # I'm assuming this means "identity" because it makes no sense otherwise
        # and will break many clients' (and our) content decoding.
        if flow.response.headers.get("Content-Encoding") == "binary/octet-stream":
            flow.response.headers["X-Broken-Content-Encoding"] = "binary/octet-stream"
            flow.response.headers["Content-Encoding"] = "identity"

    def response(self, flow: HTTPFlow):
        if flow.metadata["response_injected"]:
            return
        self._queue_flow_interception("response", flow)


class SLMITMAddon(IPCInterceptionAddon):
    def responseheaders(self, flow: HTTPFlow):
        super().responseheaders(flow)
        cap_data: typing.Optional[SerializedCapData] = flow.metadata["cap_data_ser"]

        # Request came from the proxy itself, don't touch it.
        if flow.metadata["request_injected"]:
            return

        # This is an asset server response that we're not interested in intercepting.
        # Let it stream through and don't try to buffer up the whole response body.
        if cap_data and cap_data.asset_server_cap:
            # Can't stream if we injected our own response or we were asked not to stream
            if not flow.metadata["response_injected"] and flow.metadata["can_stream"]:
                flow.response.stream = True
        elif not cap_data and not flow.metadata["from_browser"]:
            object_name = flow.response.headers.get("X-SecondLife-Object-Name", "")
            # Meh. Add some fake Cap data for this so it can be matched on.
            if object_name.startswith("#Firestorm LSL Bridge"):
                flow.metadata["cap_data_ser"] = SerializedCapData(cap_name="FirestormBridge")


class SLMITMMaster(mitmproxy.master.Master):
    def __init__(self, flow_context: HTTPFlowContext, options):
        super().__init__(options)
        self.addons.add(
            core.Core(),
            clientplayback.ClientPlayback(),
            SLMITMAddon(flow_context)
        )

    def start_server(self):
        self.start()
        asyncio.ensure_future(self.running())


def create_proxy_master(host, port, flow_context: HTTPFlowContext):  # pragma: no cover
    opts = mitmproxy.options.Options()
    master = SLMITMMaster(flow_context, opts)

    mitmproxy.options.optmanager.load_paths(
        opts,
        os.path.join(opts.confdir, "config.yaml"),
        os.path.join(opts.confdir, "config.yml"),
    )
    # Use SL's CA bundle so LL's CA certs won't cause verification errors
    ca_bundle = get_resource_filename("lib/base/network/data/ca-bundle.crt")
    opts.update(
        ssl_verify_upstream_trusted_ca=ca_bundle,
        listen_host=host,
        listen_port=port,
    )
    return master


def create_http_proxy(bind_host, port, flow_context: HTTPFlowContext):  # pragma: no cover
    master = create_proxy_master(bind_host, port, flow_context)
    pconf = SLProxyConfig(master.options)
    server = mitmproxy.proxy.server.ProxyServer(pconf)
    master.server = server
    return master


def is_asset_server_cap_name(cap_name):
    return cap_name and (
        cap_name.startswith("GetMesh")
        or cap_name.startswith("GetTexture")
        or cap_name.startswith("ViewerAsset")
    )


class SerializedCapData(typing.NamedTuple):
    cap_name: typing.Optional[str] = None
    region_addr: typing.Optional[str] = None
    session_id: typing.Optional[str] = None
    base_url: typing.Optional[str] = None
    type: str = "NORMAL"

    def __bool__(self):
        return bool(self.cap_name or self.session_id)

    @property
    def asset_server_cap(self):
        return is_asset_server_cap_name(self.cap_name)
