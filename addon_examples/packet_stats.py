import collections

from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.proxy.addon_utils import BaseAddon, GlobalProperty
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class PacketStatsAddon(BaseAddon):
    packet_stats: collections.Counter = GlobalProperty(collections.Counter)

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        self.packet_stats[message.name] += 1

    @handle_command()
    async def print_packet_stats(self, _session: Session, _region: ProxiedRegion):
        print(self.packet_stats.most_common(10))


addons = [PacketStatsAddon()]
