from __future__ import annotations

import abc
import asyncio
import collections
import ctypes
import importlib.util
import inspect
import logging
import os
import pathlib
import sys
import textwrap
import time
from types import ModuleType
from typing import *

from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.helpers import get_mtime
from hippolyzer.lib.base.message.message import Message
from hippolyzer.lib.base.network.transport import UDPPacket
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.task_scheduler import TaskLifeScope, TaskScheduler

if TYPE_CHECKING:
    from hippolyzer.lib.proxy.commands import CommandDetails, WrappedCommandCallable
    from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
    from hippolyzer.lib.proxy.object_manager import Object
    from hippolyzer.lib.proxy.region import ProxiedRegion
    from hippolyzer.lib.proxy.sessions import Session, SessionManager

LOG = logging.getLogger(__name__)


class BaseInteractionManager:
    @abc.abstractmethod
    async def open_dir(self, caption: str = '', directory: str = '', filter_str: str = '') -> Optional[str]:
        pass

    @abc.abstractmethod
    async def open_files(self, caption: str = '', directory: str = '', filter_str: str = '') -> List[str]:
        pass

    @abc.abstractmethod
    async def open_file(self, caption: str = '', directory: str = '', filter_str: str = '') -> Optional[str]:
        pass

    @abc.abstractmethod
    async def save_file(self, caption: str = '', directory: str = '', filter_str: str = '',
                        default_suffix: str = '') -> Optional[str]:
        pass

    @abc.abstractmethod
    async def confirm(self, title: str, caption: str) -> bool:
        pass

    def main_window_handle(self) -> Any:
        return None


# Used to initialize a REPL environment with commonly desired helpers
REPL_INITIALIZER = r"""
from hippolyzer.lib.base.datatypes import *
from hippolyzer.lib.base.templates import *
from hippolyzer.lib.base.message.message import Block, Message, Direction
from hippolyzer.lib.proxy.addon_utils import send_chat, show_message
"""


class AddonManager:
    COMMAND_CHANNEL = 524

    BASE_ADDON_SPECS = []
    FILE_MTIMES: Dict[str, float] = {}
    HOTRELOAD_IMPORTERS: Dict[str, set] = collections.defaultdict(set)
    FRESH_ADDON_MODULES: Dict[str, Any] = {}
    SESSION_MANAGER: Optional[SessionManager] = None
    UI: Optional[BaseInteractionManager] = None
    LAST_RELOAD = None
    SCHEDULER = TaskScheduler()
    _SUBPROCESS: bool = False
    _REPL_TASK: Optional[asyncio.Task] = None
    _HOT_RELOADING_STACK: Set[str] = set()
    _SWALLOW_ADDON_EXCEPTIONS: bool = True

    @classmethod
    def init(cls, addon_script_paths, session_manager, addon_objects=None, subprocess=False,
             swallow_addon_exceptions=True):
        addon_objects = addon_objects or []
        cls.BASE_ADDON_SPECS.clear()
        cls.FRESH_ADDON_MODULES.clear()
        cls.FILE_MTIMES.clear()
        cls.LAST_RELOAD = None
        cls.SESSION_MANAGER = session_manager
        # Are we a child process from `multiprocessing`?
        cls._SUBPROCESS = subprocess
        cls._HOT_RELOADING_STACK.clear()
        cls._SWALLOW_ADDON_EXCEPTIONS = swallow_addon_exceptions
        for path in addon_script_paths:
            # defer reloading until we've collected them all
            cls.load_addon_from_path(path, reload=False)
        for addon in addon_objects:
            cls.FRESH_ADDON_MODULES[UUID.random()] = addon
        cls._reload_addons()

    @classmethod
    def shutdown(cls):
        to_pop = []
        for mod in cls.FRESH_ADDON_MODULES.values():
            to_pop.append(mod)
            cls._call_module_hooks(mod, "handle_unload", cls.SESSION_MANAGER)
        cls.SCHEDULER.shutdown()
        for mod in to_pop:
            if isinstance(mod, ModuleType):
                sys.modules.pop(mod.__name__, None)

    @classmethod
    def have_active_repl(cls):
        return bool(cls._REPL_TASK and not cls._REPL_TASK.done())

    @classmethod
    def spawn_repl(cls, _globals=None, _locals=None, skip_frames=1) -> asyncio.Task:
        """
        Spawn a non-blocking REPL in the context of the caller's stack frame

        Execution will continue as usual after the REPL starts. If blocking is desired,
        the caller can `await` the task or run the proxy within a more suitable
        debugger like `ipdb`.

        Any REPL active when the proxy closes will be automatically cleaned up.
        """
        if cls.have_active_repl():
            raise RuntimeError("Only one active REPL allowed at a time")

        # Function-level import because this is an optional requirement
        import ptpython.repl

        # Walk up the stack and pull locals / globals from there
        stack = inspect.stack()[skip_frames]
        if _globals is None:
            _globals = stack.frame.f_globals
        if _locals is None:
            _locals = stack.frame.f_locals

        init_globals = {}
        exec(REPL_INITIALIZER, init_globals, None)
        # We're modifying the globals of the caller, be careful of things we imported
        # for the REPL initializer clobber things that already exist in the caller's globals.
        # Making our own mutable copy of the globals dict, mutating that and then passing it
        # to embed() is not an option due to https://github.com/prompt-toolkit/ptpython/issues/279
        for global_name, global_val in init_globals.items():
            if global_name not in _globals:
                _globals[global_name] = global_val

        async def _wrapper():
            coro: Coroutine = ptpython.repl.embed(  # noqa: the type signature lies
                globals=_globals,
                locals=_locals,
                return_asyncio_coroutine=True,
                patch_stdout=True,
            )
            await coro
            # Merge our changes to locals and globals back into the real stack frame
            ctypes.pythonapi.PyFrame_LocalsToFast(
                ctypes.py_object(stack.frame), ctypes.c_int(0))

        task = cls.SCHEDULER.schedule_task(_wrapper())
        cls._REPL_TASK = task
        return task

    @classmethod
    def load_addon_from_path(cls, path, reload=False, raise_exceptions=True):
        path = pathlib.Path(path).absolute()
        mod_name = "hippolyzer.user_addon_%s" % path.stem
        cls.BASE_ADDON_SPECS.append(importlib.util.spec_from_file_location(mod_name, path))
        addon_dir = os.path.realpath(pathlib.Path(path).parent.absolute())

        if addon_dir not in sys.path:
            sys.path.append(addon_dir)

        # Addon list is dirty, force a reload
        cls.LAST_RELOAD = None
        if reload:
            cls._reload_addons(raise_exceptions=raise_exceptions)

    @classmethod
    def unload_addon_from_path(cls, path, reload=False):
        path = str(pathlib.Path(path).absolute())
        specs = [x for x in cls.BASE_ADDON_SPECS if x.origin == path]
        cls.BASE_ADDON_SPECS.remove(specs[0])
        cls.FILE_MTIMES.pop(path, None)
        old_mod = cls.FRESH_ADDON_MODULES.pop(specs[0].name, None)
        if old_mod:
            cls._unload_module(old_mod)
            sys.modules.pop(old_mod.__name__, None)
        if reload:
            cls._reload_addons()

    @classmethod
    def _check_hotreloads(cls):
        """Mark addons that rely on changed files for reloading"""
        for filename, importers in cls.HOTRELOAD_IMPORTERS.items():
            mtime = get_mtime(filename)
            if not mtime or mtime == cls.FILE_MTIMES.get(filename, None):
                continue

            # Mark anything that imported this as dirty too, handling circular
            # dependencies.
            seen_importers = set()

            def _dirty_importers(cur_importers: Set[str]):
                for importer in cur_importers:
                    if importer in seen_importers:
                        continue
                    seen_importers.add(importer)
                    if importer in cls.FILE_MTIMES:
                        del cls.FILE_MTIMES[importer]
                    if importer in cls.HOTRELOAD_IMPORTERS:
                        _dirty_importers(cls.HOTRELOAD_IMPORTERS[importer])

            _dirty_importers(importers)

    @classmethod
    def hot_reload(cls, mod: Any, require_addons_loaded=False):
        # Solely to trick the type checker because ModuleType doesn't apply where it should
        # and Protocols aren't well supported yet.
        imported_mod: ModuleType = mod
        imported_file = imported_mod.__file__
        # Mark the caller as having imported (and being dependent on) `module`
        stack = inspect.stack()[1]
        cls.HOTRELOAD_IMPORTERS[imported_file].add(stack.filename)
        cls.FILE_MTIMES[imported_file] = get_mtime(imported_file)

        importing_spec = next((s for s in cls.BASE_ADDON_SPECS if s.origin == stack.filename), None)
        imported_spec = next((s for s in cls.BASE_ADDON_SPECS if s.origin == imported_file), None)

        # Both the importer and the thing being hot-reloaded are registered addons
        if imported_spec and importing_spec:
            # Bad side-effect of our fugly mixed hot-reloading code. If we hot-reload
            # an addon script from another addon, the addon objects for the imported
            # module will never be refreshed.
            if cls.BASE_ADDON_SPECS.index(importing_spec) < cls.BASE_ADDON_SPECS.index(imported_spec):
                raise ImportError(f"{imported_file} addon must be loaded before {stack.filename}"
                                  f" for hot-reloading to work correctly.")

        if require_addons_loaded and not imported_spec:
            # Some addons are dependent not only on the functions from another addon, but additionally
            # require the addons to actually be loaded.
            raise ImportError(f"{stack.filename} expected addons from {imported_file} to be loaded "
                              f"already, but they were not found!")

        # Extra guard against circular imports
        if imported_file in cls._HOT_RELOADING_STACK:
            return

        cls._HOT_RELOADING_STACK.add(imported_file)
        try:
            importlib.reload(imported_mod)
        finally:
            cls._HOT_RELOADING_STACK.remove(imported_file)

    @classmethod
    def get_loaded_script_paths(cls):
        return [s.origin for s in cls.BASE_ADDON_SPECS]

    @classmethod
    def _reload_addons(cls, raise_exceptions=False):
        if cls.LAST_RELOAD and cls.LAST_RELOAD + 2.0 > time.time():
            return
        cls.LAST_RELOAD = time.time()

        cls._check_hotreloads()

        load_exception: Optional[Exception] = None

        new_addons = {}
        for spec in cls.BASE_ADDON_SPECS[:]:
            had_mod = spec.name in cls.FRESH_ADDON_MODULES
            try:
                mtime = get_mtime(spec.origin)
                mtime_changed = mtime != cls.FILE_MTIMES.get(spec.origin, None)
                if not mtime_changed and had_mod:
                    continue
                if not mtime:
                    if not had_mod:
                        # New module and couldn't get mtime? does file exist?
                        raise RuntimeError(f"Couldn't open {spec.origin!r}")
                    else:
                        # Keep module loaded even if file went away.
                        continue

                logging.info("(Re)compiling addon %s" % spec.origin)
                old_mod = cls.FRESH_ADDON_MODULES.get(spec.name)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = mod
                spec.loader.exec_module(mod)
                cls.FILE_MTIMES[spec.origin] = mtime
                cls._unload_module(old_mod)

                new_addons[spec.name] = mod

                # Make sure module initialization happens after any pending task cancellations
                # due to module unloading.
                loop = asyncio.get_event_loop_policy().get_event_loop()
                loop.call_soon(cls._init_module, mod)
            except Exception as e:
                if had_mod:
                    logging.exception("Exploded trying to reload addon %s" % spec.name)
                    cls.FILE_MTIMES.pop(spec.loader, None)
                    cls.FRESH_ADDON_MODULES[spec.name] = None
                else:
                    logging.exception("Exploded trying to load addon %s" % spec.name)
                    cls.BASE_ADDON_SPECS.remove(spec)
                if load_exception is None:
                    load_exception = e
        cls.FRESH_ADDON_MODULES.update(new_addons)
        # if the reload was initialized by a user, let them know that a load failed.
        if raise_exceptions and load_exception is not None:
            raise load_exception

    @classmethod
    def _init_module(cls, mod: ModuleType):
        cls._call_module_hooks(mod, "handle_init", cls.SESSION_MANAGER)
        if not cls._SUBPROCESS:
            for session in cls.SESSION_MANAGER.sessions:
                with addon_ctx.push(new_session=session):
                    cls._call_module_hooks(mod, "handle_session_init", session)

    @classmethod
    def _unload_module(cls, old_mod: ModuleType):
        cls._call_module_hooks(old_mod, "handle_unload", cls.SESSION_MANAGER)
        # Kill any pending tasks that have to die with the old module
        for addon in cls._get_module_addons(old_mod):
            cls.SCHEDULER.kill_matching_tasks(lifetime_mask=TaskLifeScope.ADDON, creator=addon)

    @classmethod
    def _call_all_addon_hooks(cls, hook_name, *args, **kwargs):
        for module in cls.FRESH_ADDON_MODULES.values():
            if not module:
                continue
            ret = cls._call_module_hooks(module, hook_name, *args, **kwargs)
            if ret:
                return ret

        return None

    @classmethod
    def _get_module_addons(cls, module):
        return getattr(module, "addons", [])

    @classmethod
    def _get_all_addon_objects(cls):
        addons = []
        for module in cls.FRESH_ADDON_MODULES.values():
            # "module" might really be an addon from the extra_addons param
            addons.append(module)
            addons.extend(cls._get_module_addons(module))
        return addons

    @classmethod
    def _collect_addon_commands(cls) -> Dict[str, WrappedCommandCallable]:
        commands = {}
        for addon in cls._get_all_addon_objects():
            for name, method in inspect.getmembers(addon, predicate=inspect.ismethod):
                command = getattr(method, "command", None)
                if command is None:
                    continue
                commands[name] = method
        return commands

    @classmethod
    def _call_module_hooks(cls, module, hook_name, *args, **kwargs):
        for addon in cls._get_module_addons(module):
            ret = cls._try_call_hook(addon, hook_name, *args, **kwargs)
            if ret:
                return ret
        return cls._try_call_hook(module, hook_name, *args, **kwargs)

    @classmethod
    def _try_call_hook(cls, addon, hook_name, *args, **kwargs):
        if cls._SUBPROCESS:
            return

        if not addon:
            return
        hook_func = getattr(addon, hook_name, None)
        if not hook_func:
            return
        try:
            return hook_func(*args, **kwargs)
        except:
            logging.exception("Exploded in %r's %s hook" % (addon, hook_name))
            if not cls._SWALLOW_ADDON_EXCEPTIONS:
                raise

    @classmethod
    def _show_message(cls, text: str, session: Optional[Session] = None):
        # To deal with circular imports, need to rethink this.
        from hippolyzer.lib.proxy.addon_utils import show_message
        try:
            show_message(text, session=session)
        except:
            if not cls._SWALLOW_ADDON_EXCEPTIONS:
                raise

    @classmethod
    def _show_error(cls, text: str, session: Optional[Session] = None):
        cls._show_message(f"Error: {text}", session=session)
        LOG.error(text)

    @classmethod
    def handle_lludp_message(cls, session: Session, region: ProxiedRegion, message: Message):
        cls._reload_addons()
        if message.name == "ChatFromViewer" and "ChatData" in message:
            if message["ChatData"]["Channel"] == cls.COMMAND_CHANNEL:
                region.circuit.drop_message(message)
                with addon_ctx.push(session, region):
                    try:
                        cls._handle_command(session, region, message["ChatData"]["Message"])
                    except Exception as e:
                        LOG.exception(f'Failed while handling command {message["ChatData"]["Message"]}')
                        cls._show_message(str(e), session)
                        if not cls._SWALLOW_ADDON_EXCEPTIONS:
                            raise
                    return True
        if message.name == "ChatFromSimulator" and "ChatData" in message:
            chat: str = message["ChatData"]["Message"]
            chat_type: int = message["ChatData"]["ChatType"]
            # RLV-style OwnerSay?
            if chat and chat.startswith("@") and chat_type == 8:
                # RLV-style command, `@<cmd>(:<option1>;<option2>)?(=<param>)?`
                options, _, param = chat.rpartition("=")
                cmd, _, options = options.lstrip("@").partition(":")
                options = options.split(";")
                source = message["ChatData"]["SourceID"]
                try:
                    with addon_ctx.push(session, region):
                        handled = cls._call_all_addon_hooks("handle_rlv_command",
                                                            session, region, source, cmd, options, param)
                    if handled:
                        region.circuit.drop_message(message)
                        return True
                except:
                    LOG.exception(f"Failed while handling command {chat!r}")
                    if not cls._SWALLOW_ADDON_EXCEPTIONS:
                        raise

        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_lludp_message", session, region, message)

    @classmethod
    def _handle_command(cls, session: Session, region: ProxiedRegion, chat: str):
        commands = cls._collect_addon_commands()
        command, _, param_str = chat.partition(" ")
        if command == "help":
            help_str = "Supported commands:\n"
            for command_name, handler in commands.items():
                command_details: CommandDetails = getattr(handler, 'command')
                stringified_params = ', '.join(command_details.params.keys())
                help_str += f"{command_name}: {stringified_params}\n"
                doc = inspect.getdoc(handler)
                if doc:
                    help_str += textwrap.indent(doc, " " * 4) + "\n"

                # Viewer will truncate around 1600 bytes
                if len(help_str) > 1000:
                    cls._show_message(help_str)
                    help_str = "\n"
            if help_str.strip():
                cls._show_message(help_str)
            return

        handler: Optional[WrappedCommandCallable] = commands.get(command.lower())
        if handler is None:
            cls._show_error(f"No handler for {command!r}")
            return

        command_details: CommandDetails = getattr(handler, 'command')
        addon = getattr(handler, '__self__')
        lifetime = command_details.lifetime
        if lifetime is None:
            lifetime = TaskLifeScope.SESSION | TaskLifeScope.ADDON
        cls.SCHEDULER.schedule_task(
            coro=handler(session, region, param_str),
            scope=lifetime,
            session_id=session.id,
            creator=addon,
        )

    @classmethod
    def handle_http_request(cls, flow: HippoHTTPFlow):
        cls._reload_addons()
        session = flow.cap_data.session() if flow.cap_data.session else None
        region = flow.cap_data.region() if flow.cap_data.region else None
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_http_request", cls.SESSION_MANAGER, flow)

    @classmethod
    def handle_http_response(cls, flow: HippoHTTPFlow):
        cls._reload_addons()
        session = flow.cap_data.session() if flow.cap_data.session else None
        region = flow.cap_data.region() if flow.cap_data.region else None
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_http_response", cls.SESSION_MANAGER, flow)

    @classmethod
    def handle_eq_event(cls, session: Session, region: ProxiedRegion, event: dict):
        cls._reload_addons()
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_eq_event", session, region, event)

    @classmethod
    def handle_session_init(cls, session: Session):
        with addon_ctx.push(session):
            return cls._call_all_addon_hooks("handle_session_init", session)

    @classmethod
    def handle_session_closed(cls, session: Session):
        # kill pending tasks tied to the session
        cls.SCHEDULER.kill_matching_tasks(lifetime_mask=TaskLifeScope.SESSION, session_id=session.id)
        with addon_ctx.push(new_session=session):
            # Specifically give a strong ref so the session doesn't die until all cleanup done
            return cls._call_all_addon_hooks("handle_session_closed", session)

    @classmethod
    def handle_object_updated(cls, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str]):
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_object_updated", session, region, obj, updated_props)

    @classmethod
    def handle_object_killed(cls, session: Session, region: ProxiedRegion, obj: Object):
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_object_killed", session, region, obj)

    @classmethod
    def handle_region_changed(cls, session: Session, region: ProxiedRegion):
        # kill pending tasks tied to the main region
        cls.SCHEDULER.kill_matching_tasks(lifetime_mask=TaskLifeScope.REGION, session_id=session.id)
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_region_changed", session, region)

    @classmethod
    def handle_region_registered(cls, session: Session, region: ProxiedRegion):
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_region_registered", session, region)

    @classmethod
    def handle_circuit_created(cls, session: Session, region: ProxiedRegion):
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_circuit_created", session, region)

    @classmethod
    def handle_proxied_packet(cls, session_manager: SessionManager, packet: UDPPacket,
                              session: Optional[Session], region: Optional[ProxiedRegion]):
        with addon_ctx.push(session, region):
            return cls._call_all_addon_hooks("handle_proxied_packet", session_manager,
                                             packet, session, region)
