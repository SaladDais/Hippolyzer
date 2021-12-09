"""
Do the money dance whenever someone in the sim pays you directly
"""

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.templates import MoneyTransactionType, ChatType
from hippolyzer.lib.proxy.addon_utils import send_chat, BaseAddon
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class PaydayAddon(BaseAddon):
    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        if message.name != "MoneyBalanceReply":
            return
        transaction_block = message["TransactionInfo"][0]
        # Check for direct user -> user transfer
        if transaction_block["TransactionType"] != MoneyTransactionType.GIFT:
            return

        # Check transfer was to us, not from us
        if transaction_block["DestID"] != session.agent_id:
            return
        sender = transaction_block["SourceID"]
        if sender == session.agent_id:
            return

        # Check if they're likely to be in the sim
        sender_obj = region.objects.lookup_avatar(sender)
        if not sender_obj:
            return

        amount = transaction_block['Amount']
        send_chat(
            f"Thanks for the L${amount} secondlife:///app/agent/{sender}/completename !",
            chat_type=ChatType.SHOUT,
        )
        # Do the traditional money dance.
        session.main_region.circuit.send(Message(
            "AgentAnimation",
            Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
            Block("AnimationList", AnimID=UUID("928cae18-e31d-76fd-9cc9-2f55160ff818"), StartAnim=True),
        ))


addons = [PaydayAddon()]
