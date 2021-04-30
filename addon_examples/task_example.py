import asyncio
import datetime as dt
from typing import *

from hippolyzer.lib.proxy.addon_utils import send_chat, BaseAddon, SessionProperty
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session


class TaskExampleAddon(BaseAddon):
    chat_loop_task: Optional[asyncio.Task] = SessionProperty(None)
    chat_loop_count: Optional[int] = SessionProperty(None)
    chat_loop_started: Optional[dt.datetime] = SessionProperty(None)

    @handle_command()
    async def start_chat_task(self, session: Session, _region: ProxiedRegion):
        """Start a task that sends chat in a loop, demonstrating task scheduling"""
        # Already doing a chat loop
        if self.chat_loop_task and not self.chat_loop_task.done():
            return
        self.chat_loop_started = dt.datetime.now()
        self.chat_loop_count = 0
        # Don't need to clean this up on session shutdown because _schedule_task()
        # binds tasks to session lifetime by default
        self.chat_loop_task = self._schedule_task(self._chat_loop(session))

    @handle_command()
    async def stop_chat_task(self, _session: Session, _region: ProxiedRegion):
        """Stop the chat task if one was active"""
        if self.chat_loop_task and not self.chat_loop_task.done():
            self.chat_loop_task.cancel()
        self.chat_loop_task = None

    async def _chat_loop(self, session: Session, sleep_time=5.0):
        while True:
            region = session.main_region
            if not region:
                await asyncio.sleep(sleep_time)
                continue
            send_chat(
                f"Loop {self.chat_loop_count}, started "
                f"{dt.datetime.now() - self.chat_loop_started} ago",
                session=session
            )
            self.chat_loop_count += 1
            await asyncio.sleep(sleep_time)


addons = [TaskExampleAddon()]
