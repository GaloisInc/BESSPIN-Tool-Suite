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

import cyberphys.config as config
from cyberphys.component import ComponentPoller
from cyberphys.logger import info_logger
from cyberphys.can import CanNetwork
from cyberphys import canlib

from pygame import mixer
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, AudioSession


class InfotainmentProxy:
    """infotainment proxy between infotainment ui net and the can multiverse"""
    def __init__(self, info_net: CanNetwork, multiverse: CanNetwork):
        self._info_out = InfotainmentUi(multiverse)
        info_net.register(self._info_out)
        self._info_in = InfotainmentPlayer(info_net)
        multiverse.register(self._info_in)


class InfotainmentUi(ComponentPoller):
    """infotainment component that handles the infotainment ui net -> multiverse forwarding"""
    def __init__(self, can_network: CanNetwork):
        super().__init__("infotainment-mux", [], [])
        self._network = can_network

    @recv_can(CAN_ID_BUTTON_PRESSED, "B")
    def _(self, data):
        # forward to the other network
        self._network.send(CAN_ID_BUTTON_PRESSED, struct.pack("B", data[0]))


class InfotainmentPlayer(ComponentPoller):
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
        super().__init__("infotainment-player", [], [])
        self._network = can_network
        self._sidx: int = 0
        self._sound: typ.Union[mixer.Sound, None] = None
        self._volume = 0.0
        self._set_volume()

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

    @recv_can(canlib.CAN_ID_INFOTAINMENT_STATE, "B")
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
            self._set_volume(0.0)

    @recv_can(canlib.CAN_ID_CAR_X, "f")
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_X, struct.pack("f", data[0]))

    @recv_can(canlib.CAN_ID_CAR_Y, "f")
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_Y, struct.pack("f", data[0]))

    @recv_can(canlib.CAN_ID_CAR_Z, "f")
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_Z, struct.pack("f", data[0]))

    @recv_can(canlib.CAN_ID_CAR_R, "f")
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_R, struct.pack("f", data[0]))

