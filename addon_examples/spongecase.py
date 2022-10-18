import itertools

from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


def _to_spongecase(val):
    # give alternating casing for each character
    spongecased = itertools.zip_longest(val[::2].upper(), val[1::2].lower(), fillvalue="")
    # join them back together
    return "".join(itertools.chain(*spongecased))


def handle_lludp_message(session: Session, _region: ProxiedRegion, message: Message):
    ctx = session.addon_ctx[__name__]
    ctx.setdefault("spongecase", False)
    if message.name == "ChatFromViewer":
        chat = message["ChatData"]["Message"]
        if chat == "spongeon":
            ctx["spongecase"] = True
        elif chat == "spongeoff":
            ctx["spongecase"] = False

        if ctx["spongecase"]:
            if not chat or message["ChatData"]["Channel"] != 0:
                return
            message["ChatData"]["Message"] = _to_spongecase(chat)
