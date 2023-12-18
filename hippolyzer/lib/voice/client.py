import asyncio
import base64
import json
import logging
import random
import subprocess
import tempfile
import urllib.parse
import uuid
from collections import UserDict
from typing import Optional, Union, Any

from hippolyzer.lib.base.datatypes import Vector3
from hippolyzer.lib.base.events import Event
from hippolyzer.lib.base.message.message_handler import MessageHandler
from hippolyzer.lib.base.objects import handle_to_gridxy
from .connection import VivoxConnection

LOG = logging.getLogger(__name__)
RESP_LOG = logging.getLogger(__name__ + ".responses")


def launch_slvoice(voice_path, args, env=None):
    return subprocess.Popen([voice_path] + args, env=env)


def uuid_to_vivox(val):
    return (b"x" + base64.b64encode(uuid.UUID(val).bytes, b"-_")).decode("utf8")


def uuid_to_vivox_uri(val):
    return "sip:%s@bhr.vivox.com" % uuid_to_vivox(val)


def vivox_to_uuid(val):
    # Pull the base64-encoded UUID out of the URI
    val = val.split(":")[-1].split("@")[0][1:]
    return str(uuid.UUID(bytes=base64.b64decode(val, b"-_")))


class VoiceEvent(UserDict):
    def __init__(self, name: str, event_dict: dict):
        self.name = name
        super().__init__(event_dict)


class VoiceClient:
    SERVER_URL = "http://www.bhr.vivox.com/api2/"  # noqa

    def __init__(self, host, port):
        self._host = host
        self._port = port

        self.logged_in = Event()
        self.ready = Event()
        self.session_added = Event()
        self.channel_info_updated = Event()
        self.participant_added = Event()
        self.participant_updated = Event()
        self.participant_removed = Event()
        self.capture_devices_received = Event()

        self._pending_req_futures: dict[str, asyncio.Future] = {}

        self._connector_handle: Optional[str] = None
        self._session_handle: Optional[str] = None
        self._session_group_handle: Optional[str] = None
        self._account_handle: Optional[str] = None
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        self._display_name: Optional[str] = None
        self._uri: Optional[str] = None
        self._participants = {}

        self._mic_muted = False
        self._region_global_x = 0
        self._region_global_y = 0

        self._pos = Vector3(0, 0, 0)

        self.vivox_conn: Optional[VivoxConnection] = None
        self._poll_task = asyncio.get_event_loop().create_task(self._poll_messages())
        self.message_handler: MessageHandler[VoiceEvent, str] = MessageHandler()

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def display_name(self):
        return self._display_name

    @property
    def global_pos(self):
        return self._pos

    @property
    def region_pos(self):
        return self._global_to_region(self.global_pos)

    @property
    def uri(self):
        return self._uri

    @property
    def participants(self):
        # TODO: wrap in something to make immutable
        return self._participants

    def close(self):
        if self.vivox_conn is not None:
            self.vivox_conn.close()
        self._poll_task.cancel()
        self._poll_task = None

    async def aclose(self):
        if self._account_handle:
            await self.logout()
        self.close()

    @classmethod
    async def simple_init(
            cls,
            voice_path: str,
            host: Optional[str] = None,
            port: Optional[int] = None,
            env: Optional[dict] = None
    ):
        """Simple initializer for standing up a client"""
        if not host:
            host = "127.0.0.1"
        if not port:
            port = random.randrange(40000, 60000)

        str_addr = "%s:%s" % (host, port)
        launch_slvoice(voice_path, ["-i", str_addr, "-m", "component"], env=env)
        # HACK: wait for the process to start listening
        await asyncio.sleep(0.2)

        client = cls(host, port)
        await client.create_vivox_connection()
        await client.ready
        return client

    async def create_vivox_connection(self):
        reader, writer = await asyncio.open_connection(host=self._host, port=self._port)
        self.vivox_conn = VivoxConnection(reader, writer)

    async def create_connector(self):
        # TODO: Move all this extra crap out of here
        devices = (await self.send_message("Aux.GetCaptureDevices.1", {}))["Results"]
        self.capture_devices_received.notify(devices)

        await self.send_message("Aux.GetRenderDevices.1", {})

        await self.set_speakers_muted(False)
        await self.set_speaker_volume(62)
        await self.set_mic_muted(True)
        await self.set_mic_volume(50)

        connector_resp = await self.send_message("Connector.Create.1", {
            "ClientName": "V2 SDK",
            "AccountManagementServer": self.SERVER_URL,
            "Mode": "Normal",
            "MinimumPort": 30000,
            "MaximumPort": 50000,
            "Logging": {
                "Folder": tempfile.gettempdir(),
                "FileNamePrefix": "VivConnector",
                "FileNameSuffix": ".log",
                "LogLevel": 5
            },
            "Application": "",
            "MaxCalls": 12,
        })

        self._connector_handle = connector_resp['Results']['ConnectorHandle']
        self.ready.notify(None)

    async def login(self, username: Union[uuid.UUID, str], password: str):
        # UUID, convert to Vivox format
        if isinstance(username, uuid.UUID) or len(username) == 36:
            username = uuid_to_vivox(username)

        self._username = username
        self._password = password
        if not self._connector_handle:
            raise Exception("Need a connector handle to log in")
        if self._account_handle:
            await self.logout()

        resp = await self.send_message("Account.Login.1", {
            "ConnectorHandle": self._connector_handle,
            "AccountName": username,
            "AccountPassword": password,
            "AudioSessionAnswerMode": "VerifyAnswer",
            "EnableBuddiesAndPresence": "false",
            "BuddyManagementMode": "Application",
            "ParticipantPropertyFrequency": 5,
        })

        if resp["ReturnCode"] != 0:
            raise Exception(resp)

        self._display_name = urllib.parse.unquote(resp["Results"]["DisplayName"])
        await self.logged_in

        return resp

    async def logout(self):
        if self._session_handle:
            await self.leave_session()

        if self._account_handle:
            await self.send_message("Account.Logout.1", {
                "AccountHandle": self._account_handle,
            })
            self._account_handle = None

    async def join_session(self, uri: str, region_handle: Optional[int] = None):
        if self._session_handle:
            await self.leave_session()

        self.set_ref_region(region_handle)

        self._uri = uri

        await self.send_message("Session.Create.1", {
            "AccountHandle": self._account_handle,
            "URI": uri,
            "ConnectAudio": "true",
            "ConnectText": "false",
            "VoiceFontID": 0,
            "Name": ""
        })
        # wait until we're actually added
        await self.participant_added

    async def leave_session(self):
        await self.send_message("SessionGroup.Terminate.1", {
            "SessionGroupHandle": self._session_group_handle,
        })

        # TODO: refactor into a collection
        for participant in self._participants.values():
            self.participant_removed.notify(participant)
        self._participants.clear()
        self._session_handle = None
        self._session_group_handle = None
        self._region_global_x = 0
        self._region_global_y = 0
        self._uri = None

    def set_3d_position(self, pos: Vector3, vel: Vector3 = Vector3(0, 0, 0)) -> asyncio.Future:
        """Set global 3D position, in Vivox coordinates"""
        self._pos = pos
        future = self.send_message("Session.Set3DPosition.1", {
            "SessionHandle": self._session_handle,
            "SpeakerPosition": self._build_position_dict(pos),
            "ListenerPosition": self._build_position_dict(pos, vel=vel),
        })
        self._channel_info_updated()
        return future

    def set_region_3d_position(self, pos: Vector3, vel: Vector3 = Vector3(0, 0, 0)) -> asyncio.Future:
        """Set 3D position, in region-local coordinates"""
        vel = Vector3(vel[0], vel[2], -vel[1])
        return self.set_3d_position(self._region_to_global(pos), vel=vel)

    def set_speakers_muted(self, val: bool):
        return self.send_message("Connector.MuteLocalSpeaker.1", {
            "Value": json.dumps(val),
            "ConnectorHandle": self._connector_handle
        })

    def set_mic_muted(self, val: bool):
        self._mic_muted = val

        return self.send_message("Connector.MuteLocalMic.1", {
            "Value": json.dumps(val),
            "ConnectorHandle": self._connector_handle
        })

    def set_mic_volume(self, vol: int):
        return self.send_message("Connector.SetLocalMicVolume.1", {
            "Value": vol,
            "ConnectorHandle": self._connector_handle
        })

    def set_speaker_volume(self, vol: int):
        return self.send_message("Connector.SetLocalSpeakerVolume.1", {
            "Value": vol,
            "ConnectorHandle": self._connector_handle
        })

    def set_capture_device(self, device: str):
        return self.send_message("Aux.SetCaptureDevice.1", {
            "CaptureDeviceSpecifier": device,
        })

    def set_participant_volume(self, participant: str, vol: int):
        return self.send_message("Session.SetParticipantVolumeForMe.1", {
            "SessionHandle": self._session_handle,
            "ParticipantURI": participant,
            "Volume": vol,
        })

    async def get_channel_info(self, uri: str) -> dict:
        return await self.send_message("Account.ChannelGetInfo.1", {
            "AccountHandle": self._account_handle,
            "URI": uri
        })

    def send_web_call(self, rel_path: str, params: dict) -> asyncio.Future[dict]:
        """Make a call to a Vivox Web API"""
        return self.send_message("Account.WebCall.1", {
            "AccountHandle": self._account_handle,
            "RelativePath": rel_path,
            "Parameters": params,
        })

    def send_message(self, msg_type: str, data: Any) -> asyncio.Future[dict]:
        request_id = str(uuid.uuid4())
        # This is apparently what the viewer does, not clear if
        # request_id has any semantic significance
        if msg_type == "Session.Create.1":
            request_id = data["URI"]

        RESP_LOG.debug("%s %s %s %r" % ("Request", request_id, msg_type, data))

        asyncio.get_event_loop().create_task(self.vivox_conn.send_request(request_id, msg_type, data))
        future = asyncio.Future()
        self._pending_req_futures[request_id] = future
        return future

    def send_raw(self, data: bytes):
        return self.vivox_conn.send_raw(data)

    def set_ref_region(self, region_handle: Optional[int]):
        """Set reference position for region-local coordinates"""
        if region_handle is not None:
            self._region_global_x, self._region_global_y = handle_to_gridxy(region_handle)
        else:
            self._region_global_x, self._region_global_y = (0, 0)
        self._channel_info_updated()

    async def _poll_messages(self):
        while not self.vivox_conn:
            await asyncio.sleep(0.001)

        async for msg_type, msg_action, request_id, dict_msg in self.vivox_conn.read_messages():
            try:
                if msg_type == "Event":
                    RESP_LOG.debug("%s %s %r" % ("Event", msg_action, dict_msg))
                    self.message_handler.handle(VoiceEvent(msg_action, dict_msg))

                    # Spin off handler tasks for each event so that we don't block polling
                    _ = asyncio.get_event_loop().create_task(self._dispatch_received_event(msg_action, dict_msg))
                elif msg_type == "Response":
                    RESP_LOG.debug("%s %s %s %r" % ("Response", request_id, msg_action, dict_msg))
                    # Might not have this request ID if it was sent directly via the socket
                    if request_id in self._pending_req_futures:
                        self._pending_req_futures[request_id].set_result(dict_msg)
                        del self._pending_req_futures[request_id]
            except Exception:
                LOG.exception("Error in response handler?")

    async def _dispatch_received_event(self, event_type: str, dict_msg: dict):
        # TODO: just make these separate message handlers.
        if event_type == "VoiceServiceConnectionStateChangedEvent":
            # Vivox daemon is ready for us, create the connector
            await self.create_connector()
        elif event_type == "AccountLoginStateChangeEvent":
            if dict_msg.get('StatusString') == "OK" and dict_msg['State'] == '1':
                self._account_handle = dict_msg['AccountHandle']
                self.logged_in.notify(self._account_handle)
        elif event_type == "SessionAddedEvent":
            self._session_handle = dict_msg["SessionHandle"]
            self._session_group_handle = dict_msg["SessionGroupHandle"]
            self.session_added.notify(self._session_handle)
        elif event_type == "SessionRemovedEvent":
            self._session_handle = None
            # We often don't get all the `ParticipantRemoved`s before the session dies,
            # clear out the participant list.
            for participant in tuple(self._participants.values()):
                self._handle_participant_removed(participant)
        elif event_type == "ParticipantAddedEvent":
            self._participants[dict_msg["ParticipantUri"]] = dict_msg
            self.participant_added.notify(dict_msg)
        elif event_type == "ParticipantRemovedEvent":
            self._handle_participant_removed(dict_msg)
        elif event_type == "ParticipantUpdatedEvent":
            participant_uri = dict_msg["ParticipantUri"]
            if participant_uri in self._participants:
                self._participants[participant_uri].update(dict_msg)
                self.participant_updated.notify(dict_msg)

    def _handle_participant_removed(self, participant: dict):
        participant_uri = participant["ParticipantUri"]
        if participant_uri in self._participants:
            del self._participants[participant_uri]
            self.participant_removed.notify(participant)

    def _global_to_region(self, pos: Vector3):
        x = pos.X - self._region_global_x * 256
        z = pos.Z + self._region_global_y * 256
        # Vivox uses a different coordinate system than SL, Y is up!
        return Vector3(x, -z, pos.Y)

    def _region_to_global(self, pos: Vector3):
        x = pos.X + self._region_global_x * 256
        y = pos.Y + self._region_global_y * 256
        return Vector3(x, pos.Z, -y)

    def _build_position_dict(self, pos: Vector3, vel: Vector3 = Vector3(0, 0, 0)) -> dict:
        return {
            "Position": {
                "X": pos.X,
                "Y": pos.Y,
                "Z": pos.Z,
            },
            "Velocity": {
                "X": vel.X,
                "Y": vel.Y,
                "Z": vel.Z,
            },
            "AtOrientation": {
                "X": "1.29938e-05",
                "Y": 0,
                "Z": -1,
            },
            "UpOrientation": {
                "X": 0,
                "Y": 1,
                "Z": 0,
            },
            "LeftOrientation": {
                "X": -1,
                "Y": 0,
                "Z": "-1.29938e-05",
            }
        }

    def _channel_info_updated(self):
        pos = self.global_pos
        if self._region_global_x is not None:
            pos = self.region_pos
        self.channel_info_updated.notify(pos)
