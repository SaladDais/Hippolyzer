import enum
import logging
import typing

from PySide6 import QtCore, QtGui

from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.message_logger import FilteringMessageLogger

LOG = logging.getLogger(__name__)


class MessageLogHeader(enum.IntEnum):
    Host = 0
    Type = enum.auto()
    Method = enum.auto()
    Name = enum.auto()
    Summary = enum.auto()


class MessageLogModel(QtCore.QAbstractTableModel, FilteringMessageLogger):
    def __init__(self, parent=None, maxlen=2000):
        QtCore.QAbstractTableModel.__init__(self, parent)
        FilteringMessageLogger.__init__(self, maxlen=maxlen)

    def _begin_insert(self, insert_idx: int):
        self.beginInsertRows(QtCore.QModelIndex(), insert_idx, insert_idx)

    def _end_insert(self):
        self.endInsertRows()

    def _begin_reset(self):
        self.beginResetModel()

    def _end_reset(self):
        self.endResetModel()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._filtered_entries)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(MessageLogHeader)

    def data(self, index, role=None):
        if not index.isValid():
            return None
        entry = self._filtered_entries[index.row()]
        if role == QtCore.Qt.UserRole:
            return entry
        if role != QtCore.Qt.DisplayRole:
            return None

        col = index.column()
        val = None

        if col == MessageLogHeader.Host:
            val = entry.host
        elif col == MessageLogHeader.Method:
            val = entry.method
        elif col == MessageLogHeader.Type:
            val = entry.type
        elif col == MessageLogHeader.Name:
            val = entry.name
        elif col == MessageLogHeader.Summary:
            val = entry.summary
        return val

    def headerData(self, col, orientation, role=None):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return MessageLogHeader(col).name


class RegionListModel(QtCore.QAbstractListModel):
    def __init__(self, parent, session_manager):
        super().__init__(parent)
        self.sessionManager = session_manager
        session_manager.regionAdded.connect(self.regionAdded)
        session_manager.regionRemoved.connect(self.regionRemoved)
        self.regions: typing.List[ProxiedRegion] = session_manager.all_regions

    @QtCore.Slot(ProxiedRegion)  # noqa
    def regionAdded(self, region: ProxiedRegion):
        if region in self.regions:
            return

        num_regions = len(self.regions)
        self.beginInsertRows(QtCore.QModelIndex(), num_regions, num_regions)
        self.regions.append(region)
        self.endInsertRows()

    @QtCore.Slot(ProxiedRegion)  # noqa
    def regionRemoved(self, region: ProxiedRegion):
        try:
            region_idx = self.regions.index(region)
        except ValueError:
            return

        self.beginRemoveRows(QtCore.QModelIndex(), region_idx, region_idx)
        self.regions.remove(region)
        self.endRemoveRows()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.regions)

    def columnCount(self, parent: QtCore.QModelIndex) -> int:
        return 1

    def data(self, index, role=None):
        if not index.isValid():
            return None
        cur_region = self.regions[index.row()]
        if role == QtCore.Qt.UserRole:
            return cur_region
        elif role == QtCore.Qt.FontRole:
            for session in self.sessionManager.sessions:
                if cur_region == session.main_region:
                    font = QtGui.QFont()
                    font.setBold(True)
                    # Main region in "default" session
                    if session == self.sessionManager.sessions[-1]:
                        font.setItalic(True)
                    return font
        if role != QtCore.Qt.DisplayRole:
            return None

        col = index.column()
        val = None

        if col == 0:
            if cur_region and cur_region.session():
                val = f"{cur_region.name} ({cur_region.session().agent_id})"
            # Can happen if the weakref becomes invalid
            else:
                val = "<Dead Region>"
        return val

    def headerData(self, col, orientation, role=None):
        return None

    def clear(self):
        self.beginResetModel()
        self.regions = []
        self.endResetModel()
