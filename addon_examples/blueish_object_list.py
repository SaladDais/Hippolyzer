"""
Addon demonstrating a Qt GUI, use of the object manager and associated addon hooks

Displays a list of all objects that are mostly blue on at least one face based
on prim colors.
"""
from __future__ import annotations

import asyncio
import enum
import os.path
from typing import *

from PySide6 import QtCore, QtGui, QtWidgets

from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.objects import Object
from hippolyzer.lib.base.ui_helpers import loadUi
from hippolyzer.lib.base.templates import PCode
from hippolyzer.lib.proxy.addons import AddonManager
from hippolyzer.lib.proxy.addon_utils import BaseAddon, SessionProperty
from hippolyzer.lib.proxy.commands import handle_command
from hippolyzer.lib.base.network.transport import Direction
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session
from hippolyzer.lib.proxy.task_scheduler import TaskLifeScope


def _is_color_blueish(color: bytes) -> bool:
    # Eh this is pretty transparent.
    if color[3] < 128:
        return False

    # pretty low value, more black than anything
    if color[2] < 50:
        return False

    # Blue channel makes up at least 70% of the value
    return (color[2] / sum(color[:3])) > 0.7


def _is_object_blueish(obj: Object):
    if obj.PCode != PCode.PRIMITIVE:
        return False
    for color in obj.TextureEntry.Color.values():
        if _is_color_blueish(color):
            return True
    return False


class BlueishObjectListGUIAddon(BaseAddon):
    blueish_model: Optional[BlueishObjectModel] = SessionProperty(None)

    # Cancel the coroutine associated with this command if the region, session or addon
    # changes for any reason. Only one allowed at once across all sessions.
    @handle_command(
        single_instance=True,
        lifetime=TaskLifeScope.SESSION | TaskLifeScope.REGION | TaskLifeScope.ADDON
    )
    async def track_blueish(self, session: Session, region: ProxiedRegion):
        """Open a window that tracks blueish objects in the region"""
        parent = AddonManager.UI.main_window_handle()
        if parent is None:
            raise RuntimeError("Must be run under the GUI proxy")

        win = BlueishObjectWindow(parent, session)
        win.objectHighlightClicked.connect(self._highlight_object)  # type: ignore
        win.objectTeleportClicked.connect(self._teleport_to_object)  # type: ignore
        win.show()
        try:
            self.blueish_model = win.model
            self._scan_all_objects(session, region)
            await win.closing
            self.blueish_model = None
        except:
            # Task got killed or something exploded, close the window ourselves
            self.blueish_model = None
            win.close()
            raise

    def _highlight_object(self, session: Session, obj: Object):
        session.main_region.circuit.send(Message(
            "ForceObjectSelect",
            Block("Header", ResetList=False),
            Block("Data", LocalID=obj.LocalID),
            direction=Direction.IN,
        ))

    def _teleport_to_object(self, session: Session, obj: Object):
        session.main_region.circuit.send(Message(
            "TeleportLocationRequest",
            Block("AgentData", AgentID=session.agent_id, SessionID=session.id),
            Block(
                "Info",
                RegionHandle=session.main_region.handle,
                Position=obj.RegionPosition,
                LookAt=Vector3(0.0, 0.0, 0.0)
            ),
        ))

    def _scan_all_objects(self, _session: Session, region: ProxiedRegion):
        self.blueish_model.clear()

        for obj in region.objects.all_objects:
            if _is_object_blueish(obj):
                self.blueish_model.addObject(obj)

        obj_list = self.blueish_model.objects
        region.objects.request_object_properties([o for o in obj_list if o.Name is None])

        # Make sure we request any objects we didn't know about before,
        # they'll get picked up in the update handler.
        region.objects.request_missing_objects()

    def handle_object_updated(self, session: Session, region: ProxiedRegion,
                              obj: Object, updated_props: Set[str], msg: Optional[Message]):
        if self.blueish_model is None:
            return

        if _is_object_blueish(obj):
            if obj not in self.blueish_model:
                if obj.Name is None:
                    region.objects.request_object_properties(obj)
                self.blueish_model.addObject(obj)
            else:
                # mark the object as updated in the model,
                # fields may have changed.
                self.blueish_model.updateObject(obj)
        else:
            if obj in self.blueish_model:
                self.blueish_model.removeObject(obj)

    def handle_object_killed(self, session: Session, region: ProxiedRegion, obj: Object):
        if self.blueish_model is None:
            return
        if obj in self.blueish_model:
            self.blueish_model.removeObject(obj)


class BlueishModelHeader(enum.IntEnum):
    Name = 0
    Position = enum.auto()


class BlueishObjectModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)
        self.objects: List[Object] = []

    def __contains__(self, item):
        return item in self.objects

    def addObject(self, obj: Object):
        if obj in self.objects:
            self.updateObject(obj)
            return

        num_objs = len(self.objects)
        self.beginInsertRows(QtCore.QModelIndex(), num_objs, num_objs)
        self.objects.append(obj)
        self.endInsertRows()

    def removeObject(self, obj: Object):
        try:
            obj_idx = self.objects.index(obj)
        except ValueError:
            return

        self.beginRemoveRows(QtCore.QModelIndex(), obj_idx, obj_idx)
        self.objects.remove(obj)
        self.endRemoveRows()

    def updateObject(self, obj: Object):
        try:
            obj_idx = self.objects.index(obj)
        except ValueError:
            return
        top_left = self.createIndex(obj_idx, 1)
        bottom_right = self.createIndex(obj_idx, self.columnCount())
        self.dataChanged.emit(top_left, bottom_right)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.objects)

    def columnCount(self, parent: QtCore.QModelIndex = None) -> int:
        return len(BlueishModelHeader)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        obj = self.objects[index.row()]
        if role == QtCore.Qt.UserRole:
            return obj
        if role != QtCore.Qt.DisplayRole:
            return None

        col = index.column()
        val = None

        if col == BlueishModelHeader.Name:
            val = obj.Name or ""
        elif col == BlueishModelHeader.Position:
            try:
                val = str(obj.RegionPosition)
            except ValueError:
                # If the object is orphaned we may not be able to figure
                # out the region pos
                val = "Unknown"

        return val

    def headerData(self, col, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return BlueishModelHeader(col).name

    def clear(self):
        self.beginResetModel()
        self.objects = []
        self.endResetModel()


BLUEISH_UI_PATH = os.path.join(os.path.dirname(__file__), "blueish_object_list.ui")


class BlueishObjectWindow(QtWidgets.QMainWindow):
    objectHighlightClicked = QtCore.Signal(Session, Object)
    objectTeleportClicked = QtCore.Signal(Session, Object)

    tableView: QtWidgets.QTableView

    def __init__(self, parent, session: Session):
        self.closing = asyncio.Future()
        super().__init__(parent=parent)
        loadUi(BLUEISH_UI_PATH, self)
        self.model = BlueishObjectModel(self)
        self.session = session
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().resizeSection(BlueishModelHeader.Name, 150)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.buttonHighlight.clicked.connect(self._highlightClicked)
        self.buttonTeleport.clicked.connect(self._teleportClicked)

    def closeEvent(self, event: QtGui.QCloseEvent):
        if not self.closing.done():
            self.closing.set_result(True)
        super().closeEvent(event)

    def _highlightClicked(self):
        self._emitForSelectedObject(self.objectHighlightClicked)

    def _teleportClicked(self):
        self._emitForSelectedObject(self.objectTeleportClicked)

    def _emitForSelectedObject(self, signal: QtCore.Signal):
        object_indexes = self.tableView.selectionModel().selectedIndexes()
        if not object_indexes:
            return
        obj = object_indexes[0].data(QtCore.Qt.UserRole)
        signal.emit(self.session, obj)  # type: ignore


addons = [BlueishObjectListGUIAddon()]
