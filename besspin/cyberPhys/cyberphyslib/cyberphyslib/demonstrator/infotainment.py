"""
Project: SSITH CyberPhysical Demonstrator
Name: infotainment.py
Author: Ethan Lew <elew@galois.com>
Date: 01/21/2020

Infotainment Proxy Component

The infotainment proxy is responsible for:
    1. Accepting CAN packets from the infotainment server state regarding button presses and station
    changes

    2. Playing relevant music files associated with each station

    3. Adjusting the system volume in response to volume button presses

    4. Forwarding the infotainment packet to the active CAN network
"""
import glob
import os
import pathlib
import struct
import typing as typ

import cyberphyslib.demonstrator.config as config
import cyberphyslib.demonstrator.component as ccomp
from cyberphyslib.demonstrator.logger import info_logger
from cyberphyslib.demonstrator.can import CanNetwork
from cyberphyslib.canlib.canspecs import *
import cyberphyslib.canlib.canspecs as canspecs
import enum

from pygame import mixer
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, AudioSession


class InfotainmentProxy:
    """infotainment proxy between infotainment ui net and the can multiverse"""
    def __init__(self, info_net: CanNetwork, multiverse: CanNetwork):
        self.info_ui = InfotainmentUi(multiverse)
        info_net.register(self.info_ui)
        self.info_player = InfotainmentPlayer(info_net)
        #multiverse.register(self.info_player)


class InfotainmentUiStatus(enum.IntEnum):
    READY = enum.auto()


class InfotainmentPlayerStatus(enum.IntEnum):
    READY = enum.auto()


class InfotainmentUi(ccomp.ComponentPoller):
    """infotainment component that handles the infotainment ui net -> multiverse forwarding"""
    def __init__(self, can_network: CanNetwork):
        super().__init__("infoui", [(config.DIRECTOR_PORT, 'infoui-commands')], [(config.INFO_UI_PORT, 'infoui-events'),
                                                                                 (config.INFO_UI_PORT, 'infoui-beamng')])
        self._network = can_network

    def on_start(self):
        self.send_message(ccomp.Message(InfotainmentUiStatus.READY), "infoui-events")

    @recv_can(canspecs.CAN_ID_BUTTON_PRESSED,canspecs.CAN_FORMAT_BUTTON_PRESSED)
    def _(self, data):
        # alert simulator to turn off self driving mode
        from cyberphyslib.demonstrator.simulator import BeamNgCommand
        self.send_message(ccomp.Message(BeamNgCommand.UI_BUTTON_PRESSED), "infoui-beamng")
        # forward to the other network
        self._network.send(canspecs.CAN_ID_BUTTON_PRESSED, struct.pack(canspecs.CAN_FORMAT_BUTTON_PRESSED, data[0]))


class InfotainmentPlayer(ccomp.ComponentPoller):
    """infotainment component that handles the multiverse -> ui net forwarding and music mixer"""
    stations = glob.glob(str(pathlib.Path(config.RADIO_SOUND_DIR) / r'bensound-*.mp3'))

    session_pid = os.getpid()

    vol_increment = 0.1

    vol_range = 2 ** 5

    @staticmethod
    def get_named_session(name: str) -> typ.Union[AudioSession, None]:
        """get an audio session with a specific process name

        NOTE:this might be inefficient -- this approach was taken from
        the pycaw source
        """
        for session in AudioUtilities.GetAllSessions():
            if session.Process:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                if session.Process.name() == name:
                    return session, volume
        return None

    def __init__(self, can_network: CanNetwork):
        super().__init__("infoplay", [(config.DIRECTOR_PORT, 'infoplay-commands')], [(config.INFO_PLAY_PORT, 'infoplay-events')])
        self._network = can_network
        self._sidx: int = 0
        self._sound: typ.Union[mixer.Sound, None] = None
        self._volume = 0.5
        self._set_volume()
        self.play_sound()

    def on_start(self):
        self.send_message(ccomp.Message(InfotainmentPlayerStatus.READY), "infoplay-events")

    def on_exit(self):
        if self._sound:
            self._sound.stop()

    def play_sound(self):
        """play sound file depending on station select"""
        if self._sound is not None:
            self._sound.stop()
        mixer.init()
        mixer.get_init()
        self._sound = mixer.Sound(
            str(self.stations[self._sidx])
        )
        self._sound.play(loops=-1)
        self._set_volume()

    def _set_volume(self):
        """find audio session and set the master volume given the volume state"""
        if self._sound is None:
            self.play_sound()
        session = AudioUtilities.GetProcessSession(self.session_pid)
        if session:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(self._volume, None)
        else:
            raise RuntimeError(f"audio session doesn't exist!")

    @recv_can(canspecs.CAN_ID_INFOTAINMENT_STATE, canspecs.CAN_FORMAT_INFOTAINMENT_STATE)
    def _(self, data):
        """respond to the infotainment button press"""
        # decode the incoming value
        val = data[0]
        music_playing: bool = (0x1 & val) == 1
        val >>= 1
        station = 0x3 & val
        val >>= 2
        volume = val
        assert station <= 0x3, f"station number isn't valid {station}"

        # apply music mixer actions
        if music_playing:
            target_volume = volume / self.vol_range
            if self._volume != target_volume:
                info_logger.info(f"changing volume to {target_volume} %%")
                self._volume = target_volume
                self._set_volume()
            if self._sidx != station - 1 or self._sound is None:
                info_logger.info(f"changing station to {self._sidx} index")
                self._sidx = station - 1
                self.play_sound()
        else:
            if self._sound is not None:
                self._sound.stop()
            self._volume = 0
            self._set_volume()

    @recv_can(canspecs.CAN_ID_CAR_X, canspecs.CAN_FORMAT_CAR_X)
    def _(self, data):
        self._network.send(canspecs.CAN_ID_CAR_X, struct.pack(canspecs.CAN_FORMAT_CAR_X, data[0]))

    @recv_can(canspecs.CAN_ID_CAR_Y, canspecs.CAN_FORMAT_CAR_Y)
    def _(self, data):
        self._network.send(canspecs.CAN_ID_CAR_Y, struct.pack(canspecs.CAN_FORMAT_CAR_Y, data[0]))

    @recv_can(canspecs.CAN_ID_CAR_Z, canspecs.CAN_FORMAT_CAR_Z)
    def _(self, data):
        self._network.send(canspecs.CAN_ID_CAR_Z, struct.pack(canspecs.CAN_FORMAT_CAR_Z, data[0]))

    @recv_can(canspecs.CAN_ID_CAR_R, canspecs.CAN_FORMAT_CAR_R)
    def _(self, data):
        self._network.send(canspecs.CAN_ID_CAR_R, struct.pack(canspecs.CAN_FORMAT_CAR_R, data[0]))

