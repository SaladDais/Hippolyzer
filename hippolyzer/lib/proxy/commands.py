from __future__ import annotations

import asyncio
import functools
import threading
from typing import *

from hippolyzer.lib.proxy.task_scheduler import TaskLifeScope

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.region import ProxiedRegion
    from hippolyzer.lib.proxy.sessions import Session
    WrappedCommandCallable = Callable[[Session, ProxiedRegion, str], Coroutine]


class Parameter(NamedTuple):
    parser: Callable[[str], Any] = str
    # None makes this greedy
    sep: Optional[str] = " "
    optional: bool = False


class CommandDetails(NamedTuple):
    name: str
    params: Dict[str, Parameter]
    lifetime: Optional[TaskLifeScope] = None


def parse_bool(val: str) -> bool:
    return val.lower() in ('on', 'true', '1', '1.0', 'yes')


def handle_command(command_name: Optional[str] = None, /, *, lifetime: Optional[TaskLifeScope] = None,
                   single_instance: bool = False, **params: Union[Parameter, callable]):
    """
    Register a coroutinefunction as a handler for a named command

    The function's name will be used if a name is not provided.
    """
    def _command_wrapper(func: Callable[..., Coroutine]):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError(f"{func!r} is not async!")

        if single_instance:
            inner_func = func
            lock = threading.Lock()

            @functools.wraps(inner_func)
            async def func(self, *args, **kwargs):
                if lock.acquire(blocking=False):
                    try:
                        return await inner_func(self, *args, **kwargs)
                    finally:
                        lock.release()
                else:
                    raise RuntimeError(f"{inner_func.__name__} is already running")

        @functools.wraps(func)
        def _inner(self, session: Session, region: ProxiedRegion, message: str) -> Coroutine:
            param_vals = {}
            for param_name, param in params.items():
                # can do foo=str, bar=int
                if callable(param):
                    param = Parameter(parser=param)
                # Greedy, takes the rest of the message
                if param.sep is None:
                    param_val = message
                    message = ""
                else:
                    message = message.lstrip(param.sep)
                    if not message:
                        if not param.optional:
                            raise KeyError(f"Missing parameter {param_name}")
                        continue
                    param_val, _, message = message.partition(param.sep)  # type: ignore

                param_vals[param_name] = param.parser(param_val)

            return func(self, session, region, **param_vals)

        _inner.command = CommandDetails(
            name=command_name or func.__name__,
            lifetime=lifetime,
            params={k: v or Parameter() for (k, v) in params.items()},
        )
        return _inner
    return _command_wrapper
