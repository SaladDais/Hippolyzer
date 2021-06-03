import asyncio
import base64
import email
import functools
import html
import itertools
import json
import logging
import pathlib
import multiprocessing
import re
import signal
import socket
import sys
import urllib.parse
from typing import *

import multidict
from qasync import QEventLoop
from PySide2 import QtCore, QtWidgets, QtGui

from hippolyzer.apps.model import MessageLogModel, MessageLogHeader, RegionListModel
from hippolyzer.apps.proxy import start_proxy
from hippolyzer.lib.base import llsd
from hippolyzer.lib.base.datatypes import UUID
from hippolyzer.lib.base.helpers import bytes_unescape, bytes_escape, get_resource_filename
from hippolyzer.lib.base.message.llsd_msg_serializer import LLSDMessageSerializer
from hippolyzer.lib.base.message.message import Block, Message
from hippolyzer.lib.base.message.message_formatting import (
    HumanMessageSerializer,
    VerbatimHumanVal,
    subfield_eval,
    SpannedString,
)
from hippolyzer.lib.base.message.msgtypes import MsgType
from hippolyzer.lib.base.message.template_dict import TemplateDictionary
from hippolyzer.lib.base.ui_helpers import loadUi
import hippolyzer.lib.base.serialization as se
from hippolyzer.lib.base.network.transport import Direction, WrappingUDPTransport
from hippolyzer.lib.proxy.addons import BaseInteractionManager, AddonManager
from hippolyzer.lib.proxy.ca_utils import setup_ca_everywhere
from hippolyzer.lib.proxy.caps_client import ProxyCapsClient
from hippolyzer.lib.proxy.http_proxy import create_proxy_master, HTTPFlowContext
from hippolyzer.lib.proxy.message_logger import LLUDPMessageLogEntry, AbstractMessageLogEntry
from hippolyzer.lib.proxy.region import ProxiedRegion
from hippolyzer.lib.proxy.sessions import Session, SessionManager
from hippolyzer.lib.proxy.templates import CAP_TEMPLATES

LOG = logging.getLogger(__name__)

MAIN_WINDOW_UI_PATH = get_resource_filename("apps/proxy_mainwindow.ui")
MESSAGE_BUILDER_UI_PATH = get_resource_filename("apps/message_builder.ui")
ADDON_DIALOG_UI_PATH = get_resource_filename("apps/addon_dialog.ui")
FILTER_DIALOG_UI_PATH = get_resource_filename("apps/filter_dialog.ui")


def show_error_message(error_msg, parent=None):
    error_dialog = QtWidgets.QErrorMessage(parent=parent)
    # No obvious way to set this to plaintext, yuck...
    error_dialog.showMessage(html.escape(error_msg))
    error_dialog.exec_()
    error_dialog.raise_()


class GUISessionManager(SessionManager, QtCore.QObject):
    regionAdded = QtCore.Signal(ProxiedRegion)
    regionRemoved = QtCore.Signal(ProxiedRegion)

    def __init__(self, model):
        SessionManager.__init__(self)
        QtCore.QObject.__init__(self)
        self.all_regions = []
        self.message_logger = model

    def checkRegions(self):
        new_regions = itertools.chain(*[s.regions for s in self.sessions])
        new_regions = [r for r in new_regions if r.is_alive]
        for new_region in new_regions:
            if new_region not in self.all_regions:
                self.regionAdded.emit(new_region)  # type: ignore
        for old_region in self.all_regions:
            if old_region not in new_regions:
                self.regionRemoved.emit(old_region)  # type: ignore

        self.all_regions = new_regions


class GUIInteractionManager(BaseInteractionManager, QtCore.QObject):
    def __init__(self, parent):
        BaseInteractionManager.__init__(self)
        QtCore.QObject.__init__(self, parent=parent)

    def main_window_handle(self) -> Any:
        return self.parent()

    def _dialog_async_exec(self, dialog: QtWidgets.QDialog):
        future = asyncio.Future()
        dialog.finished.connect(lambda r: future.set_result(r))
        dialog.open()
        return future

    async def _file_dialog(self, caption: str, directory: str, filter_str: str, mode: QtWidgets.QFileDialog.FileMode) \
            -> Tuple[bool, QtWidgets.QFileDialog]:
        dialog = QtWidgets.QFileDialog(self.parent(), caption=caption, directory=directory, filter=filter_str)
        dialog.setFileMode(mode)
        if mode == QtWidgets.QFileDialog.FileMode.AnyFile:
            dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        res = await self._dialog_async_exec(dialog)
        return res, dialog

    async def open_files(self, caption: str = '', directory: str = '', filter_str: str = '') -> List[str]:
        res, dialog = await self._file_dialog(
            caption, directory, filter_str, QtWidgets.QFileDialog.FileMode.ExistingFiles
        )
        if not res:
            return []
        return dialog.selectedFiles()

    async def open_file(self, caption: str = '', directory: str = '', filter_str: str = '') -> Optional[str]:
        res, dialog = await self._file_dialog(
            caption, directory, filter_str, QtWidgets.QFileDialog.FileMode.ExistingFile
        )
        if not res:
            return None
        return dialog.selectedFiles()[0]

    async def open_dir(self, caption: str = '', directory: str = '', filter_str: str = '') -> Optional[str]:
        res, dialog = await self._file_dialog(
            caption, directory, filter_str, QtWidgets.QFileDialog.FileMode.Directory
        )
        if not res:
            return None
        return dialog.selectedFiles()[0]

    async def save_file(self, caption: str = '', directory: str = '', filter_str: str = '') -> Optional[str]:
        res, dialog = await self._file_dialog(
            caption, directory, filter_str, QtWidgets.QFileDialog.FileMode.AnyFile
        )
        if not res or not dialog.selectedFiles():
            return None
        return dialog.selectedFiles()[0]


def nonFatalExceptions(f):
    @functools.wraps(f)
    def _wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            logging.exception("Treating exception as non-fatal")
            show_error_message(str(e), parent=self)
            return None

    return _wrapper


class ProxyGUI(QtWidgets.QMainWindow):
    DEFAULT_IGNORE = "StartPingCheck CompletePingCheck PacketAck SimulatorViewerTimeMessage SimStats " \
                     "AgentUpdate AgentAnimation AvatarAnimation ViewerEffect CoarseLocationUpdate LayerData " \
                     "CameraConstraint ObjectUpdateCached RequestMultipleObjects ObjectUpdate ObjectUpdateCompressed " \
                     "ImprovedTerseObjectUpdate KillObject ImagePacket SoundTrigger AttachedSound PreloadSound " \
                     "GetMesh GetMesh2 EventQueueGet RequestObjectPropertiesFamily ObjectPropertiesFamily " \
                     "AvatarRenderInfo FirestormBridge ObjectAnimation ParcelDwellRequest ParcelAccessListRequest " \
                     "ParcelDwellReply ParcelAccessListReply AttachedSoundGainChange " \
                     "ParcelPropertiesRequest ParcelProperties GetObjectCost GetObjectPhysicsData ObjectImage " \
                     "ViewerAsset GetTexture SetAlwaysRun GetDisplayNames MapImageService MapItemReply".split(" ")
    DEFAULT_FILTER = f"!({' || '.join(ignored for ignored in DEFAULT_IGNORE)})"

    textRequest: QtWidgets.QTextEdit

    def __init__(self):
        super().__init__()
        loadUi(MAIN_WINDOW_UI_PATH, self)

        self.settings = QtCore.QSettings("SaladDais", "hippolyzer")
        self._selectedEntry: Optional[AbstractMessageLogEntry] = None

        self.model = MessageLogModel(parent=self.tableView)
        self.tableView.setModel(self.model)
        self.model.rowsAboutToBeInserted.connect(self.beforeInsert)
        self.model.rowsInserted.connect(self.afterInsert)
        self.tableView.selectionModel().selectionChanged.connect(self._messageSelected)
        self.checkBeautify.clicked.connect(self._showSelectedMessage)
        self.checkPause.clicked.connect(self._setPaused)
        self._setFilter(self.DEFAULT_FILTER)
        self.btnClearLog.clicked.connect(self.model.clear)
        self.lineEditFilter.editingFinished.connect(self._setFilter)
        self.btnMessageBuilder.clicked.connect(self._sendToMessageBuilder)
        self.btnCopyRepr.clicked.connect(self._copyRepr)
        self.actionInstallHTTPSCerts.triggered.connect(self._installHTTPSCerts)
        self.actionManageAddons.triggered.connect(self._manageAddons)
        self.actionManageFilters.triggered.connect(self._manageFilters)
        self.actionOpenMessageBuilder.triggered.connect(self._openMessageBuilder)
        self.actionProxyRemotelyAccessible.setChecked(
            self.settings.value("RemotelyAccessible", False, type=bool))
        self.actionUseViewerObjectCache.setChecked(
            self.settings.value("UseViewerObjectCache", False, type=bool))
        self.actionProxyRemotelyAccessible.triggered.connect(self._setProxyRemotelyAccessible)
        self.actionUseViewerObjectCache.triggered.connect(self._setUseViewerObjectCache)

        self._filterMenu = QtWidgets.QMenu()
        self._populateFilterMenu()
        self.toolButtonFilter.setMenu(self._filterMenu)

        self.sessionManager = GUISessionManager(self.model)
        self.interactionManager = GUIInteractionManager(self)
        AddonManager.UI = self.interactionManager

        self._shouldScrollOnInsert = True
        self.tableView.horizontalHeader().resizeSection(MessageLogHeader.Host, 80)
        self.tableView.horizontalHeader().resizeSection(MessageLogHeader.Method, 60)
        self.tableView.horizontalHeader().resizeSection(MessageLogHeader.Name, 180)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.textResponse.hide()

    def _populateFilterMenu(self):
        def _addFilterAction(text, filter_str):
            filter_action = QtWidgets.QAction(text, self)
            filter_action.triggered.connect(lambda: self._setFilter(filter_str))
            self._filterMenu.addAction(filter_action)

        self._filterMenu.clear()

        _addFilterAction("Default", self.DEFAULT_FILTER)
        filters = self.getFilterDict()
        for preset_name, preset_filter in filters.items():
            _addFilterAction(preset_name, preset_filter)

    def getFilterDict(self):
        return json.loads(str(self.settings.value("Filters", "{}")))

    def setFilterDict(self, val: dict):
        self.settings.setValue("Filters", json.dumps(val))
        self._populateFilterMenu()

    def _manageFilters(self):
        dialog = FilterDialog(self)
        dialog.exec_()

    @nonFatalExceptions
    def _setFilter(self, filter_str=None):
        if filter_str is None:
            filter_str = self.lineEditFilter.text()
        else:
            self.lineEditFilter.setText(filter_str)
        self.model.set_filter(filter_str)

    def _setPaused(self, checked):
        self.model.set_paused(checked)

    def _messageSelected(self, selected, _deselected):
        indexes = selected.indexes()
        if not len(indexes):
            self.btnMessageBuilder.setEnabled(False)
            self.btnCopyRepr.setEnabled(False)
            return
        index = indexes[0]
        entry: AbstractMessageLogEntry = index.data(QtCore.Qt.UserRole)
        self._selectedEntry = entry
        self.btnMessageBuilder.setEnabled(True)
        if isinstance(entry, LLUDPMessageLogEntry):
            self.btnCopyRepr.setEnabled(True)
        else:
            self.btnCopyRepr.setEnabled(False)
        self._showSelectedMessage()

    def _showSelectedMessage(self):
        entry = self._selectedEntry
        if not entry:
            return
        req = entry.request(
            beautify=self.checkBeautify.isChecked(),
            replacements=self.buildReplacements(entry.session, entry.region),
        )
        highlight_range = None
        if isinstance(req, SpannedString):
            match_result = self.model.filter.match(entry)
            # Match result was a tuple indicating what matched
            if isinstance(match_result, tuple):
                highlight_range = req.spans.get(match_result)

        self.textRequest.setPlainText(req)
        if highlight_range:
            cursor = self.textRequest.textCursor()
            cursor.setPosition(highlight_range[0], QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(highlight_range[1], QtGui.QTextCursor.KeepAnchor)
            highlight_format = QtGui.QTextBlockFormat()
            highlight_format.setBackground(QtCore.Qt.yellow)
            cursor.setBlockFormat(highlight_format)

        resp = entry.response(beautify=self.checkBeautify.isChecked())
        if resp:
            self.textResponse.show()
            self.textResponse.setPlainText(resp)
        else:
            self.textResponse.hide()

    def beforeInsert(self):
        vbar = self.tableView.verticalScrollBar()
        self._shouldScrollOnInsert = vbar.value() == vbar.maximum()

    def afterInsert(self):
        if self._shouldScrollOnInsert:
            self.tableView.scrollToBottom()

    def _sendToMessageBuilder(self):
        if not self._selectedEntry:
            return
        win = MessageBuilderWindow(self, self.sessionManager)
        win.show()
        msg = self._selectedEntry
        beautify = self.checkBeautify.isChecked()
        replacements = self.buildReplacements(msg.session, msg.region)
        win.setMessageText(msg.request(beautify=beautify, replacements=replacements))

    @nonFatalExceptions
    def _copyRepr(self):
        if not self._selectedEntry:
            return
        if not isinstance(self._selectedEntry, LLUDPMessageLogEntry):
            return
        msg_repr = self._selectedEntry.message.repr(pretty=True)
        QtGui.QGuiApplication.clipboard().setText(msg_repr)

    def _openMessageBuilder(self):
        win = MessageBuilderWindow(self, self.sessionManager)
        win.show()

    def buildReplacements(self, session: Session, region: ProxiedRegion):
        if not session or not region:
            return {}
        selected = session.selected
        agent_object = region.objects.lookup_fullid(session.agent_id)
        selected_local = selected.object_local
        selected_object = None
        if selected_local:
            # We may or may not have an object for this
            selected_object = region.objects.lookup_localid(selected_local)
        return {
            "SELECTED_LOCAL": selected_local,
            "SELECTED_FULL": selected_object.FullID if selected_object else None,
            "SELECTED_PARCEL_LOCAL": selected.parcel_local,
            "SELECTED_PARCEL_FULL": selected.parcel_full,
            "SELECTED_SCRIPT_ITEM": selected.script_item,
            "SELECTED_TASK_ITEM": selected.task_item,
            "AGENT_ID": session.agent_id,
            "AGENT_LOCAL": agent_object.LocalID if agent_object else None,
            "SESSION_ID": session.id,
            "AGENT_POS": agent_object.Position if agent_object else None,
            "NULL_KEY": UUID(),
            "RANDOM_KEY": UUID.random,
            "CIRCUIT_CODE": session.circuit_code,
            "REGION_HANDLE": region.handle,
        }

    def _installHTTPSCerts(self):
        msg = QtWidgets.QMessageBox()
        msg.setText("This will install the proxy's HTTPS certificate in the config dir"
                    " of any installed viewers, continue?")
        yes_btn = msg.addButton("Yes", QtWidgets.QMessageBox.NoRole)
        msg.addButton("No", QtWidgets.QMessageBox.NoRole)
        msg.exec()
        clicked_btn = msg.clickedButton()
        if clicked_btn is not yes_btn:
            return

        master = create_proxy_master("127.0.0.1", -1, HTTPFlowContext())
        dirs = setup_ca_everywhere(master)

        msg = QtWidgets.QMessageBox()
        if dirs:
            msg.setText(f"Installed certificate in {[str(x) for x in dirs]!r}, restart your viewer!")
        else:
            msg.setText("Couldn't find any viewer config directories!")
        msg.exec()

    def _setProxyRemotelyAccessible(self, checked: bool):
        self.settings.setValue("RemotelyAccessible", checked)
        msg = QtWidgets.QMessageBox()
        msg.setText("Remote accessibility setting changes will take effect on next run")
        msg.exec()

    def _setUseViewerObjectCache(self, checked: bool):
        self.settings.setValue("UseViewerObjectCache", checked)
        self.sessionManager.use_viewer_object_cache = checked

    def _manageAddons(self):
        dialog = AddonDialog(self)
        dialog.exec_()

    def getAddonList(self) -> List[str]:
        return json.loads(str(self.settings.value("Addons", "[]")))

    def setAddonList(self, val: List[str]):
        self.settings.setValue("Addons", json.dumps(val))


BANNED_HEADERS = ("content-length", "host")


def _parse_http_message(msg_text):
    request_line, mime_msg = re.split(r"\r?\n", msg_text, 1)
    method, uri, version = msg_text.split(" ", 2)
    # comment line for URI, throw it out.
    while mime_msg.startswith("#"):
        _, mime_msg = re.split(r"\r?\n", mime_msg, 1)
    msg = email.message_from_string(mime_msg)
    # Throw out Content-Length, very likely to be wrong after beautification
    headers = multidict.CIMultiDict(
        (k, v) for k, v in msg.items() if k.lower() not in BANNED_HEADERS
    )
    # Use to get the body rather than `email.` since that wants to do some
    # fancy parsing of MIME bits that we don't want it to do.
    msg_parts = re.split(r"\r?\n\r?\n", msg_text, 1)
    body = None
    if len(msg_parts) == 2:
        body = msg_parts[1]
    return method, uri, headers, body


def _coerce_to_bytes(val):
    if isinstance(val, bytes):
        return val
    if not isinstance(val, str):
        val = str(val)
    return val.encode("utf8")


class MessageBuilderWindow(QtWidgets.QMainWindow):
    def __init__(self, parent, session_manager):
        super().__init__(parent=parent)
        loadUi(MESSAGE_BUILDER_UI_PATH, self)
        self.templateDict = TemplateDictionary()
        self.llsdSerializer = LLSDMessageSerializer()
        self.sessionManager: SessionManager = session_manager
        self.regionModel = RegionListModel(self, self.sessionManager)
        self.listRegions.setModel(self.regionModel)

        self._populateMessageTypeMenus()
        self.comboTrusted.textActivated.connect(self._fillUDPMessage)
        self.comboUntrusted.textActivated.connect(self._fillUDPMessage)
        self.comboCaps.textActivated.connect(self._fillCapsMessage)

        self.btnSend.clicked.connect(self._sendMessage)
        self.textRequest.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

    def _getTarget(self):
        region_indexes = self.listRegions.selectionModel().selectedIndexes()
        session, region = None, None
        if region_indexes:
            region = region_indexes[0].data(QtCore.Qt.UserRole)
            session = region.session()
        elif self.sessionManager.sessions:
            session = self.sessionManager.sessions[-1]
            region = session.main_region
        return session, region

    def setMessageText(self, text):
        self.textRequest.setPlainText(text)

    def _populateMessageTypeMenus(self):
        self.comboTrusted.clear()
        self.comboUntrusted.clear()
        self.comboCaps.clear()

        self.comboTrusted.addItem("<Trusted>")
        self.comboUntrusted.addItem("<Untrusted>")
        self.comboCaps.addItem("<Caps>")

        message_names = sorted(x.name for x in self.templateDict)

        for message_name in message_names:
            if self.templateDict[message_name].msg_trust:
                self.comboTrusted.addItem(message_name)
            else:
                self.comboUntrusted.addItem(message_name)

        cap_names = sorted(set(itertools.chain(*[r.caps.keys() for r in self.regionModel.regions])))
        for cap_name in cap_names:
            if cap_name.endswith("ProxyWrapper"):
                continue
            self.comboCaps.addItem(cap_name)

    def _fillCapsMessage(self, cap_name):
        if cap_name.startswith("<"):
            return
        session, region = self._getTarget()
        self.textRequest.clear()
        params = ""
        path = ""
        body = "<llsd><undef/></llsd>"
        method = "POST"
        headers = "Content-Type: application/llsd+xml\nX-Hippo-Directives: 1\n"
        for cap_template in CAP_TEMPLATES:
            # Might be nice to allow selecting method variants?
            if cap_template.cap_name == cap_name:
                params = urllib.parse.urlencode({x: '' for x in cap_template.query})
                if params:
                    params = '?' + params
                body = cap_template.body.decode("utf8")
                path = cap_template.path
                method = cap_template.method
                if method == "GET":
                    # No content-type because no content
                    headers = ""
                break
        self.textRequest.setPlainText(
            f"""{method} [[{cap_name}]]{path}{params} HTTP/1.1
# {region.caps.get(cap_name, "<unknown URI>")}
{headers}
{body}"""
        )

    def _fillUDPMessage(self, message_name):
        if message_name.startswith("<"):
            return
        self.textRequest.clear()

        template = self.templateDict[message_name]
        msg = Message(message_name, direction=Direction.OUT)

        for tmpl_block in template.blocks:
            num_blocks = tmpl_block.number or 1
            for i in range(num_blocks):
                fill_vars = {}
                for var in tmpl_block.variables:
                    fill_vars[var.name] = self._getVarPlaceholder(template, tmpl_block, var)
                msg_block = Block(tmpl_block.name, **fill_vars)
                msg.add_block(msg_block)
        self.textRequest.setPlainText(
            HumanMessageSerializer.to_human_string(msg, replacements={}, beautify=True, template=template)
        )

    def _getVarPlaceholder(self, msg, block, var):
        if block.name == "AgentData":
            if var.name == "AgentID":
                return VerbatimHumanVal("[[AGENT_ID]]")
            if var.name == "SessionID":
                return VerbatimHumanVal("[[SESSION_ID]]")
        if block.name == "ObjectData":
            if var.name.endswith("ID") and var.name != "AgentID":
                if var.type == MsgType.MVT_LLUUID:
                    return VerbatimHumanVal("[[SELECTED_FULL]]")
                else:
                    return VerbatimHumanVal("[[SELECTED_LOCAL]]")
        if "Parcel" in msg.name:
            if var.name.endswith("LocalID"):
                return VerbatimHumanVal("[[SELECTED_PARCEL_LOCAL]]")
        if "ParcelID" in var.name:
            return VerbatimHumanVal("[[SELECTED_PARCEL_FULL]]")
        if "Handle" in var.name:
            return VerbatimHumanVal("[[REGION_HANDLE]]")
        if "CircuitCode" in var.name or ("Circuit" in block.name and "Code" in var.name):
            return VerbatimHumanVal("[[CIRCUIT_CODE]]")
        if var.name.endswith("LocalID"):
            return VerbatimHumanVal("[[SELECTED_LOCAL]]")
        if any(var.name.endswith(x) for x in ("TransactionID", "TransferID", "Invoice", "QueryID")):
            return VerbatimHumanVal("[[RANDOM_KEY]]")
        if var.name in ("TaskID", "ObjectID"):
            return VerbatimHumanVal("[[SELECTED_FULL]]")

        if var.type.is_int:
            return 0
        elif var.type.is_float:
            return 0.0
        elif var.type == MsgType.MVT_LLUUID:
            return UUID()
        elif var.type == MsgType.MVT_BOOL:
            return False
        elif var.type == MsgType.MVT_VARIABLE:
            return ""
        elif var.type in (MsgType.MVT_LLVector3, MsgType.MVT_LLVector3d, MsgType.MVT_LLQuaternion):
            return VerbatimHumanVal("(0.0, 0.0, 0.0)")
        elif var.type == MsgType.MVT_LLVector4:
            return VerbatimHumanVal("(0.0, 0.0, 0.0, 0.0)")
        elif var.type == MsgType.MVT_FIXED:
            return b"\x00" * var.size
        elif var.type == MsgType.MVT_IP_ADDR:
            return "0.0.0.0"
        return VerbatimHumanVal("")

    @nonFatalExceptions
    def _sendMessage(self, _checked=False):
        session, region = self._getTarget()

        msg_text = self.textRequest.toPlainText()
        replacements = self.parent().buildReplacements(session, region)

        if re.match(r"\A\s*(in|out)\s+", msg_text, re.I):
            sender_func = self._sendLLUDPMessage
        elif re.match(r"\A\s*(eq)\s+", msg_text, re.I):
            sender_func = self._sendEQMessage
        elif re.match(r"\A.*http/[0-9.]+\r?\n", msg_text, re.I):
            sender_func = self._sendHTTPMessage
        else:
            raise ValueError("IDK what kind of message %s is" % msg_text)

        for i in range(0, self.spinRepeat.value() + 1):
            sender_func(session, region, msg_text, {"i": i, **replacements})

    def _buildEnv(self, session, region):
        env = {}
        if region:
            env["full_to_local"] = lambda x: region.objects.lookup_fullid(x).LocalID
            env["region"] = region
        if session:
            env["session"] = session
        return env

    def _sendLLUDPMessage(self, session, region: Optional[ProxiedRegion], msg_text, replacements):
        if not session or not region:
            raise RuntimeError("Need a valid session and region to send LLUDP")
        env = self._buildEnv(session, region)
        # We specifically want to allow `eval()` in messages since
        # messages from here are trusted.
        msg = HumanMessageSerializer.from_human_string(msg_text, replacements, env, safe=False)
        if self.checkLLUDPViaCaps.isChecked():
            if msg.direction == Direction.IN:
                region.eq_manager.queue_event(
                    self.llsdSerializer.serialize(msg, as_dict=True)
                )
            else:
                self._sendHTTPRequest(
                    "POST",
                    region.caps["UntrustedSimulatorMessage"],
                    {"Content-Type": "application/llsd+xml", "Accept": "application/llsd+xml"},
                    self.llsdSerializer.serialize(msg),
                )
        else:
            transport = None
            off_circuit = self.checkOffCircuit.isChecked()
            if off_circuit:
                transport = WrappingUDPTransport(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
            region.circuit.send_message(msg, transport=transport)
            if off_circuit:
                transport.close()

    def _sendEQMessage(self, session, region: Optional[ProxiedRegion], msg_text: str, _replacements: dict):
        if not session or not region:
            raise RuntimeError("Need a valid session and region to send EQ event")
        message_line, _, body = (x.strip() for x in msg_text.partition("\n"))
        message_name = message_line.rsplit(" ", 1)[-1]
        region.eq_manager.queue_event({
            "message": message_name,
            "body": llsd.parse_xml(body.encode("utf8")),
        })

    def _sendHTTPMessage(self, session, region, msg_text: str, replacements: dict):
        env = self._buildEnv(session, region)
        method, uri, headers, body = _parse_http_message(msg_text)

        has_directives = headers.get("X-Hippo-Directives") == "1"
        is_escaped = headers.get("X-Hippo-Escaped-Body") == "1"
        is_beautified = headers.get("X-Hippo-Beautify") == "1"

        if body:
            body = body.encode("utf8")
            # Only handle directives if specifically asked for
            if has_directives:
                def directive_handler(m):
                    return self._handleHTTPDirective(env, replacements, is_escaped, m)
                body = re.sub(rb"<!HIPPO(\w+)\[\[(.*?)]]>", directive_handler, body, flags=re.S)
        match = re.match(r"\A\[\[(.*?)]](.*)", uri)
        cap_name = None
        if match:
            cap_name = match.group(1)
            cap_url = session.global_caps.get(cap_name)
            if not cap_url:
                cap_url = region.caps.get(cap_name)
            if not cap_url:
                raise ValueError("Don't have a Cap for %s" % cap_name)
            uri = cap_url + match.group(2)

        # The body contains python escape sequences, decode them.
        if is_escaped:
            body = bytes_unescape(body)

        # Convert from human-friendly representation before sending
        if cap_name and is_beautified:
            parsed = llsd.parse_xml(body)
            serializer = se.HTTP_SERIALIZERS.get(cap_name)
            if serializer:
                body = serializer.serialize_req_body(method, parsed)
                if body is se.UNSERIALIZABLE:
                    raise ValueError(f"Cannot serialize {parsed!r}")

        headers.pop("X-Hippo-Beautify", None)
        headers.pop("X-Hippo-Directives", None)
        headers.pop("X-Hippo-Escaped-Body", None)
        self._sendHTTPRequest(method, uri, headers, body)

    def _handleHTTPDirective(self, env: dict, replacements: dict, need_escaped: bool, match: re.Match) -> bytes:
        # HTTP messages from the builder can have inline directives like
        # <!HIPPOBASE64[[foobar]]>, handle those.
        directive: bytes = match.group(1)
        contents: bytes = match.group(2)
        unescaped_contents: bytes = bytes_unescape(contents)

        if directive == b"BASE64":
            val = base64.b64encode(unescaped_contents)
        elif directive == b"CDATA":
            val = contents.replace(b"&", b"&amp;").replace(b"<", b"&lt;").replace(b">", b"&gt;")
        elif directive == b"UNESCAPE":
            val = unescaped_contents
        elif directive == b"EVAL":
            val = subfield_eval(contents.decode("utf8").strip(), globals_={**env, **replacements})
            val = _coerce_to_bytes(val)
        elif directive == b"REPL":
            val = _coerce_to_bytes(replacements[contents.decode("utf8").strip()])
        else:
            raise ValueError(f"Unknown directive {directive}")

        # We're going to output this in a context that expects string escape sequences
        # This isn't very nice, but saves me writing a parser for the language in HTTP
        # request bodies.
        if need_escaped:
            return bytes_escape(val)
        return val

    def _sendHTTPRequest(self, method, uri, headers, body):
        caps_client = ProxyCapsClient()

        async def _send_request():
            req = caps_client.request(method, uri, headers=headers, data=body)
            async with req as resp:
                # Read, but throw away the resp so the connection is kept alive long
                # enough for the full response to pass through the proxy
                await resp.read()

        asyncio.create_task(_send_request())


class AddonDialog(QtWidgets.QDialog):
    listAddons: QtWidgets.QListWidget

    def __init__(self, parent: ProxyGUI):
        super().__init__()

        loadUi(ADDON_DIALOG_UI_PATH, self)
        self._parent = parent
        self.btnLoad.pressed.connect(self._loadPressed)
        self.btnRemove.pressed.connect(self._removeCurrentPressed)
        self._populateAddons()

    def _populateAddons(self):
        for addon in self._parent.getAddonList():
            self.listAddons.addItem(QtWidgets.QListWidgetItem(addon))

    @nonFatalExceptions
    def _removeCurrentPressed(self):
        selected = self.listAddons.selectedItems()
        if selected:
            item: QtWidgets.QListWidgetItem = selected[0]
            try:
                AddonManager.unload_addon_from_path(item.text(), reload=True)
            except Exception as e:
                # This addon might not even really be loaded
                show_error_message(error_msg=str(e), parent=self)
            addons = self._parent.getAddonList()
            addons.remove(item.text())
            self._parent.setAddonList(addons)
            idx = self.listAddons.indexFromItem(item).row()
            self.listAddons.takeItem(idx)

    @nonFatalExceptions
    def _loadPressed(self):
        file_filter = 'Python Addon (*.py)'

        options = QtWidgets.QFileDialog.Options()
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load', '', file_filter, options=options)
        if not path:
            return
        addons = self._parent.getAddonList()
        path = str(pathlib.Path(path).absolute())
        # already loaded
        if path in addons:
            return
        AddonManager.load_addon_from_path(path, reload=True)
        addons.append(path)
        self.listAddons.addItem(QtWidgets.QListWidgetItem(path))
        self._parent.setAddonList(addons)


class FilterDialog(QtWidgets.QDialog):
    listFilters: QtWidgets.QListWidget

    def __init__(self, parent: ProxyGUI):
        super().__init__()

        loadUi(FILTER_DIALOG_UI_PATH, self)
        self._parent = parent
        self.btnSaveCurrent.pressed.connect(self._saveCurrent)
        self.btnRemove.pressed.connect(self._removeCurrentPressed)
        self._populateFilters()

    def _populateFilters(self):
        self.listFilters.clear()
        for filter_obj in self._parent.getFilterDict():
            self.listFilters.addItem(QtWidgets.QListWidgetItem(filter_obj))

    @nonFatalExceptions
    def _saveCurrent(self):
        filters = self._parent.getFilterDict()
        filter_text = self._parent.lineEditFilter.text()
        name, ok = QtWidgets.QInputDialog.getText(self, "Filter Name", "Filter Name",
                                                  QtWidgets.QLineEdit.EchoMode.Normal)
        if not name or not ok:
            return
        filters[name] = filter_text
        self._parent.setFilterDict(filters)
        self._populateFilters()

    @nonFatalExceptions
    def _removeCurrentPressed(self):
        selected = self.listFilters.selectedItems()
        if selected:
            item: QtWidgets.QListWidgetItem = selected[0]
            filters = self._parent.getFilterDict()
            del filters[item.text()]
            self._parent.setFilterDict(filters)
            idx = self.listFilters.indexFromItem(item).row()
            self.listFilters.takeItem(idx)


def gui_main():
    multiprocessing.set_start_method('spawn')
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = ProxyGUI()
    timer = QtCore.QTimer(app)
    timer.timeout.connect(window.sessionManager.checkRegions)
    timer.start(100)
    signal.signal(signal.SIGINT, lambda *args: QtWidgets.QApplication.quit())
    window.show()
    remote_access = window.settings.value("RemotelyAccessible", False, type=bool)
    use_vocache = window.settings.value("UseViewerObjectCache", False, type=bool)
    window.sessionManager.use_viewer_object_cache = use_vocache
    http_host = None
    if remote_access:
        http_host = "0.0.0.0"
    start_proxy(
        session_manager=window.sessionManager,
        extra_addon_paths=window.getAddonList(),
        proxy_host=http_host,
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    gui_main()
