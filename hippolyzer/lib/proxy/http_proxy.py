import asyncio
import logging
import multiprocessing
import os
import re
import sys
import queue
import typing
import uuid
import weakref

import mitmproxy.certs
import mitmproxy.ctx
import mitmproxy.log
import mitmproxy.master
import mitmproxy.options
import mitmproxy.proxy
from mitmproxy.addons import core, clientplayback, proxyserver, next_layer, disable_h2c
from mitmproxy.http import HTTPFlow
from mitmproxy.proxy.layers import tls
import OpenSSL

from hippolyzer.lib.base.helpers import get_resource_filename
from hippolyzer.lib.base.multiprocessing_utils import ParentProcessWatcher
from hippolyzer.lib.proxy.caps import SerializedCapData


class SLCertStore(mitmproxy.certs.CertStore):
    def get_cert(self, commonname: typing.Optional[str], sans: typing.List[str], *args, **kwargs):
        entry = super().get_cert(commonname, sans, *args, **kwargs)
        cert, privkey, chain = entry.cert, entry.privatekey, entry.chain_file
        x509 = cert.to_pyopenssl()
        # The cert must have a subject key ID or the viewer will reject it.
        for i in range(0, x509.get_extension_count()):
            ext = x509.get_extension(i)
            # This cert already has a subject key id, pass through.
            if ext.get_short_name() == b"subjectKeyIdentifier":
                return entry

        # The viewer doesn't actually use the subject key ID for its intended purpose,
        # so a random, unique value is fine.
        x509.add_extensions([
            OpenSSL.crypto.X509Extension(
                b"subjectKeyIdentifier",
                False,
                uuid.uuid4().hex.encode("utf8"),
            ),
        ])
        x509.sign(OpenSSL.crypto.PKey.from_cryptography_key(privkey), "sha256")  # type: ignore
        new_entry = mitmproxy.certs.CertStoreEntry(
            mitmproxy.certs.Cert.from_pyopenssl(x509), privkey, chain
        )
        # Replace the cert that was created in the base `get_cert()` with our modified cert
        self.certs[(commonname, tuple(sans))] = new_entry
        self.expire_queue.pop(-1)
        self.expire(new_entry)
        return new_entry


class SLTlsConfig(mitmproxy.addons.tlsconfig.TlsConfig):
    def running(self):
        super().running()
        old_cert_store = self.certstore
        # Replace the cert store with one that knows how to add
        # a subject key ID extension.
        self.certstore = SLCertStore(
            default_privatekey=old_cert_store.default_privatekey,
            default_ca=old_cert_store.default_ca,
            default_chain_file=old_cert_store.default_chain_file,
            dhparams=old_cert_store.dhparams,
        )
        self.certstore.certs = old_cert_store.certs

    def tls_start_server(self, tls_start: tls.TlsData):
        super().tls_start_server(tls_start)
        # Since 2000 the recommendation per RFCs has been to only check SANs and not the CN field.
        # Most browsers do this, as does mitmproxy. The viewer does not, and the sim certs have no SAN
        # field. set the host verification flags to remove the flag that disallows falling back to
        # checking the CN (X509_CHECK_FLAG_NEVER_CHECK_SUBJECT)
        param = OpenSSL.SSL._lib.SSL_get0_param(tls_start.ssl_conn._ssl)  # noqa
        # get_hostflags() doesn't seem to be exposed, just set the usual flags without
        # the problematic `X509_CHECK_FLAG_NEVER_CHECK_SUBJECT` flag.
        flags = OpenSSL.SSL._lib.X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS  # noqa
        OpenSSL.SSL._lib.X509_VERIFY_PARAM_set_hostflags(param, flags)  # noqa


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
        self.mitmproxy_ready = flow_context.mitmproxy_ready
        self.flows: weakref.WeakValueDictionary[str, HTTPFlow] = weakref.WeakValueDictionary()
        self.from_proxy_queue: multiprocessing.Queue = flow_context.from_proxy_queue
        self.to_proxy_queue: multiprocessing.Queue = flow_context.to_proxy_queue
        self.shutdown_signal: multiprocessing.Event = flow_context.shutdown_signal

    def add_log(self, entry: mitmproxy.log.LogEntry):
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
        # Tell the main process mitmproxy is ready to handle requests
        self.mitmproxy_ready.set()

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
                    orig_flow = self.flows[flow_id]
                    orig_flow.set_state(flow_state)
                elif event_type == "preempt":
                    orig_flow = self.flows.get(flow_id)
                    if orig_flow:
                        orig_flow.intercept()
                        orig_flow.set_state(flow_state)
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
        was_injected = flow.request.headers.pop("X-Hippo-Injected", "")
        if was_injected == "1" and not from_browser:
            flow.metadata["request_injected"] = True

        # Does this request need the stupid hack around aiohttp's windows proactor bug
        need_ssl_hack = flow.request.headers.pop("X-Hippo-Windows-SSL-Hack", None) == "1"
        if need_ssl_hack and sys.platform == "win32":
            flow.request.url = re.sub(r"^http:", "https:", flow.request.url)
        self._queue_flow_interception("request", flow)

    def _queue_flow_interception(self, event_type: str, flow: HTTPFlow):
        flow.intercept()
        self.flows[flow.id] = flow
        self.from_proxy_queue.put((event_type, flow.get_state()), True)

    def responseheaders(self, flow: HTTPFlow):
        # The response was injected earlier in an earlier handler,
        # we don't want to touch this anymore.
        if flow.metadata.get("response_injected"):
            return

        # Someone fucked up and put a mimetype in Content-Encoding.
        # I'm assuming this means "identity" because it makes no sense otherwise
        # and will break many clients' (and our) content decoding.
        if flow.response.headers.get("Content-Encoding") == "binary/octet-stream":
            flow.response.headers["X-Broken-Content-Encoding"] = "binary/octet-stream"
            flow.response.headers["Content-Encoding"] = "identity"

    def response(self, flow: HTTPFlow):
        cap_data: typing.Optional[SerializedCapData] = flow.metadata.get("cap_data")
        if flow.metadata.get("response_injected") and cap_data and cap_data.asset_server_cap:
            # Don't bother intercepting asset server requests where we injected a response.
            # We don't want to log them and they don't need any more processing by user hooks.
            return
        self._queue_flow_interception("response", flow)


class SLMITMAddon(IPCInterceptionAddon):
    def responseheaders(self, flow: HTTPFlow):
        super().responseheaders(flow)
        cap_data: typing.Optional[SerializedCapData] = flow.metadata.get("cap_data_ser")

        # Request came from the proxy itself, don't touch it.
        if flow.metadata.get("request_injected"):
            return

        # This is an asset server response that we're not interested in intercepting.
        # Let it stream through and don't try to buffer up the whole response body.
        if cap_data and cap_data.asset_server_cap:
            # Can't stream if we injected our own response or we were asked not to stream
            if not flow.metadata["response_injected"] and flow.metadata["can_stream"]:
                flow.response.stream = True
        elif not cap_data and not flow.metadata.get("from_browser"):
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
            disable_h2c.DisableH2C(),
            proxyserver.Proxyserver(),
            next_layer.NextLayer(),
            SLTlsConfig(),
            SLMITMAddon(flow_context),
        )


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
    return master
