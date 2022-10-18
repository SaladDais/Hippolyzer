from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


def handle_lludp_message(session: Session, region: ProxiedRegion, message: Message):
    # addon_ctx will persist across addon reloads, use for storing data that
    # needs to survive across calls to this function
    ctx = session.addon_ctx[__name__]
    if message.name == "ChatFromViewer":
        chat = message["ChatData"]["Message"]
        if chat == "COUNT":
            ctx["chat_counter"] = ctx.get("chat_counter", 0) + 1
            message["ChatData"]["Message"] = str(ctx["chat_counter"])
