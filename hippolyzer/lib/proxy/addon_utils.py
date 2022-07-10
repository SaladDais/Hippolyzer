import abc
import copy
import dataclasses
import multiprocessing
import pickle
import secrets
import warnings
from typing import *

from hippolyzer.lib.base.datatypes import UUID, Vector3
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.proxy import addon_ctx
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.http_flow import HippoHTTPFlow
from hippolyzer.lib.base.network.transport import UDPPacket, Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import SessionManager, Session
from hippolyzer.lib.proxy.task_scheduler import TaskLifeScope
from hippolyzer.lib.base.templates import ChatSourceType, ChatType


class AssetAliasTracker:
    def __init__(self):
        # Mapping of real asset UUID -> fake asset UUID
        self.alias_mapping: Dict[UUID, UUID] = {}
        # The inverse
        self.rev_mapping: Dict[UUID, UUID] = {}

    def invalidate_aliases(self):
        # Only clear the real -> alias map so we can still do lookups
        # on stale aliases, but assets will receive new aliases.
        self.alias_mapping.clear()

    def clear(self):
        self.alias_mapping.clear()
        self.rev_mapping.clear()

    def get_orig_uuid(self, val: UUID) -> Optional[UUID]:
        return self.rev_mapping.get(val)

    def get_alias_uuid(self, val: UUID, create: bool = True) -> Optional[UUID]:
        if create:
            alias_id = self.alias_mapping.setdefault(val, UUID.random())
        else:
            alias_id = self.alias_mapping.get(val)
            if alias_id is None:
                return None
        self.rev_mapping.setdefault(alias_id, val)
        return alias_id


def show_message(text, session=None) -> None:
    """Convenience function for showing a message to the user"""
    if not isinstance(text, (bytes, str)):
        text = repr(text)

    # `or None` so we don't use a dead weakref Proxy which are False-y
    session = session or addon_ctx.session.get(None) or None
    message = Message(
        "ChatFromSimulator",
        Block(
            "ChatData",
            FromName="Hippolyzer",
            SourceID=UUID(),
            OwnerID=UUID(),
            SourceType=ChatSourceType.SYSTEM,
            ChatType=ChatType.OWNER,
            Audible=True,
            Position=Vector3(),
            Message=text,
        ),
        direction=Direction.IN,
    )
    if session:
        session.main_region.circuit.send(message)
    else:
        for session in AddonManager.SESSION_MANAGER.sessions:
            session.main_region.circuit.send(copy.copy(message))


def send_chat(message: Union[bytes, str], channel=0, chat_type=ChatType.NORMAL, session=None):
    session = session or addon_ctx.session.get(None) or None
    if not session:
        raise RuntimeError("Tried to send chat without session")
    session.main_region.circuit.send(Message(
        "ChatFromViewer",
        Block(
            "AgentData",
            AgentID=session.agent_id,
            SessionID=session.id,
        ),
        Block(
            "ChatData",
            Message=message,
            Channel=channel,
            Type=chat_type,
        ),
    ))


def ais_item_to_inventory_data(ais_item: dict):
    return Block(
        "InventoryData",
        ItemID=ais_item["item_id"],
        FolderID=ais_item["parent_id"],
        CallbackID=0,
        CreatorID=ais_item["permissions"]["creator_id"],
        OwnerID=ais_item["permissions"]["owner_id"],
        GroupID=ais_item["permissions"]["group_id"],
        BaseMask=ais_item["permissions"]["base_mask"],
        OwnerMask=ais_item["permissions"]["owner_mask"],
        GroupMask=ais_item["permissions"]["group_mask"],
        EveryoneMask=ais_item["permissions"]["everyone_mask"],
        NextOwnerMask=ais_item["permissions"]["next_owner_mask"],
        GroupOwned=0,
        AssetID=ais_item["asset_id"],
        Type=ais_item["type"],
        InvType=ais_item["inv_type"],
        Flags=ais_item["flags"],
        SaleType=ais_item["sale_info"]["sale_type"],
        SalePrice=ais_item["sale_info"]["sale_price"],
        Name=ais_item["name"],
        Description=ais_item["desc"],
        CreationDate=ais_item["created_at"],
        # Meaningless here
        CRC=secrets.randbits(32),
    )


def ais_folder_to_inventory_data(ais_folder: dict):
    return Block(
        "FolderData",
        FolderID=ais_folder["cat_id"],
        ParentID=ais_folder["parent_id"],
        CallbackID=0,
        Type=ais_folder["preferred_type"],
        Name=ais_folder["name"],
    )


class BaseAddon(abc.ABC):
    def _schedule_task(self, coro: Coroutine, session=None,
                       region_scoped=False, session_scoped=True, addon_scoped=True):
        session = session or addon_ctx.session.get(None) or None
        scope = TaskLifeScope(0)
        if region_scoped:
            if not session:
                raise ValueError("Must pass a session object when scheduling a region-scoped task")
            scope |= TaskLifeScope.REGION
        if session_scoped:
            if not session:
                raise ValueError("Must pass a session object when scheduling a session-scoped task")
            scope |= TaskLifeScope.SESSION
        if addon_scoped:
            scope |= TaskLifeScope.ADDON

        session_id = None if not session else session.id
        return AddonManager.SCHEDULER.schedule_task(coro, scope, session_id, self)

    def handle_init(self, session_manager: SessionManager):
        pass

    def handle_session_init(self, session: Session):
        pass

    def handle_session_closed(self, session: Session):
        pass

    def handle_unload(self, session_manager: SessionManager):
        pass

    def handle_lludp_message(self, session: Session, region: ProxiedRegion, message: Message):
        pass

    def handle_http_request(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        pass

    def handle_http_response(self, session_manager: SessionManager, flow: HippoHTTPFlow):
        pass

    def handle_eq_event(self, session: Session, region: ProxiedRegion, event: dict):
        pass

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str]):
        pass

    def handle_object_killed(self, session: Session, region: ProxiedRegion, obj: Object):
        pass

    def handle_region_changed(self, session: Session, region: ProxiedRegion):
        pass

    def handle_region_registered(self, session: Session, region: ProxiedRegion):
        pass

    def handle_circuit_created(self, session: Session, region: ProxiedRegion):
        pass

    def handle_rlv_command(self, session: Session, region: ProxiedRegion, source: UUID,
                           cmd: str, options: List[str], param: str):
        pass

    def handle_proxied_packet(self, session_manager: SessionManager, packet: UDPPacket,
                              session: Optional[Session], region: Optional[ProxiedRegion]):
        pass


_T = TypeVar("_T")
_U = TypeVar("_U", Session, SessionManager)


class BaseAddonProperty(abc.ABC, Generic[_T, _U]):
    """
    Special property added to Addons that persists value across addon reloads

    Currently works by transparently writing to the session.addon_ctx or
    session_manager.addon_ctx dict, without any namespacing. Can be accessed either
    through `AddonClass.property_name` or `addon_instance.property_name`.
    """
    __slots__ = ("name", "default")

    def __init__(self, default=dataclasses.MISSING):
        self.default = default

    def __set_name__(self, owner, name: str):
        self.name = name

    def _make_default(self) -> _T:
        if self.default is not dataclasses.MISSING:
            if callable(self.default):
                return self.default()
            return self.default
        return dataclasses.MISSING

    @abc.abstractmethod
    def _get_context_obj(self) -> Optional[_U]:
        raise NotImplementedError()

    def __get__(self, _obj, owner: Optional[Type] = None) -> _T:
        ctx_obj = self._get_context_obj()
        if ctx_obj is None:
            raise AttributeError(
                f"{self.__class__} {self.name} accessed outside proper context")
        # Set a default if we have one, otherwise let the keyerror happen.
        # Maybe we should do this at addon initialization instead of on get.
        if self.name not in ctx_obj.addon_ctx:
            default = self._make_default()
            if default is not dataclasses.MISSING:
                ctx_obj.addon_ctx[self.name] = default
            else:
                raise AttributeError(f"{self.name} is not set")
        return ctx_obj.addon_ctx[self.name]

    def __set__(self, _obj, value: _T) -> None:
        self._get_context_obj().addon_ctx[self.name] = value


class SessionProperty(BaseAddonProperty[_T, Session]):
    """
    Property tied to the current session context

    Survives across addon reloads
    """
    def _get_context_obj(self) -> Optional[Session]:
        return addon_ctx.session.get()


class GlobalProperty(BaseAddonProperty[_T, SessionManager]):
    """
    Property tied to the global SessionManager context

    Survives across addon reloads
    """
    def _get_context_obj(self) -> SessionManager:
        return AddonManager.SESSION_MANAGER


class AddonProcess(multiprocessing.Process, multiprocessing.process.BaseProcess):
    """
    Wrapper for multiprocessing targets defined in dynamically loaded addons

    multiprocessing will unpickle target and args before any user code has run in its
    spawned process. If target is in a dynamically loaded module (like an addon) the
    unpickle will throw and starting the process will fail. We wrap the original target
    in a function that imports the scripts for any loaded addons before attempting to
    unpickle the inner target function reference.

    Does not work with args or kwargs of types defined in dynamically loaded modules.
    Doing so would require special-casing of multiprocessing's objects. Event, Queue,
    and others cannot be pickled normally.
    """
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None,
                 *, daemon=None):
        kwargs = kwargs or {}
        pickled_target = pickle.dumps(target, protocol=pickle.HIGHEST_PROTOCOL)
        script_paths = AddonManager.get_loaded_script_paths()
        super().__init__(group=group, target=self._target_wrapper, name=name,
                         args=(pickled_target, script_paths) + args, kwargs=kwargs, daemon=daemon)

    @staticmethod
    def _target_wrapper(pickled_target: bytes, script_paths: Sequence[str], *args, **kwargs):
        warnings.simplefilter("ignore")
        AddonManager.init(script_paths, session_manager=None, subprocess=True)
        target = pickle.loads(pickled_target)
        return target(*args, **kwargs)
