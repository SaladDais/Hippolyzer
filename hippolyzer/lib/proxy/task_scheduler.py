import asyncio
import enum
import weakref
from typing import *

from hippolyzer.lib.base.datatypes import UUID


class TaskLifeScope(enum.Flag):
    """Task should be automatically canceled when data related to flag is changed"""
    # Cancel task when session is closed
    SESSION = enum.auto()
    # Cancel task when _main_ region changes
    REGION = enum.auto()
    # Cancel task when the object that created it (usually an addon) is unloaded
    # (all tasks are canceled when proxy is closed regardless)
    ADDON = enum.auto()


class TaskLifeData:
    def __init__(
            self,
            scope: TaskLifeScope,
            session_id: Optional[UUID] = None,
            creator: Optional[Any] = None,
    ):
        if scope & (TaskLifeScope.REGION | TaskLifeScope.SESSION) and not session_id:
            raise ValueError(f"{scope!r} requires non-null session_id")
        elif scope & TaskLifeScope.ADDON and not creator:
            raise ValueError(f"{scope!r} requires non-null creator addon object")

        # Region-scoped implies session-scoped
        if scope & TaskLifeScope.REGION:
            scope |= TaskLifeScope.SESSION
        self.scope = scope
        self.session_id = session_id
        # only needed for looking for tasks created by this object
        self.creator = weakref.proxy(creator) if creator else None


class TaskScheduler:
    def __init__(self):
        self.tasks: List[Tuple[TaskLifeData, asyncio.Task]] = []

    @staticmethod
    async def _ignore_coro_cancellation(coro: Coroutine):
        try:
            await coro
        except asyncio.CancelledError:
            # If the task didn't handle its own CancelledError
            # then we don't care.
            pass

    def schedule_task(self, coro: Coroutine, scope: Optional[TaskLifeScope] = None,
                      session_id: Optional[UUID] = None, creator: Any = None):
        scope = scope or TaskLifeScope(0)
        task_data = TaskLifeData(scope, session_id, creator)
        task = asyncio.create_task(self._ignore_coro_cancellation(coro))
        task.add_done_callback(self._task_done)
        self.tasks.append((task_data, task))
        return task

    def shutdown(self):
        for task_data, task in self.tasks:
            task.cancel()

        try:
            event_loop = asyncio.get_running_loop()
            await_all = asyncio.gather(*(task for task_data, task in self.tasks))
            event_loop.run_until_complete(await_all)
        except RuntimeError:
            pass
        self.tasks.clear()

    def _task_done(self, task: asyncio.Task):
        for task_details in reversed(self.tasks):
            if task == task_details[1]:
                self.tasks.remove(task_details)
                break

    def get_matching_tasks(self, creator=None, session_id=None):
        for task_data, task in self.tasks[:]:
            if creator and creator == task_data.creator:
                yield task_data, task
            elif session_id and session_id == task_data.session_id:
                yield task_data, task

    def kill_matching_tasks(self, lifetime_mask: TaskLifeScope, **kwargs):
        for task_data, task in self.get_matching_tasks(**kwargs):
            if task_data.scope & lifetime_mask:
                task.cancel()
