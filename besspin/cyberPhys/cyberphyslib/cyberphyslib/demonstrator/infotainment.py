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
import enum

import cyberphyslib.demonstrator.config as config
import cyberphyslib.demonstrator.component as ccomp
from cyberphyslib.demonstrator.logger import info_logger
from cyberphyslib.demonstrator.can import CanNetwork
from cyberphyslib.demonstrator.simulator import BeamNgCommand
import cyberphyslib.canlib as canlib

from pygame import mixer
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, AudioSession

class InfotainmentProxy:
    """infotainment proxy between infotainment ui net and the can multiverse"""
    def __init__(self, info_net: CanNetwork, multiverse: CanNetwork):
        self.info_ui = InfotainmentUi(multiverse)
        self.info_player = InfotainmentPlayer(info_net)


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

    # TODO: test and add this?
    # # This should enable switching from self-drive when a button is pressed
    # @recv_can(canlib.CAN_ID_BUTTON_PRESSED,canlib.CAN_FORMAT_BUTTON_PRESSED)
    # def _(self, data):
    #     # alert simulator to turn off self driving mode
    #     self.send_message(ccomp.Message(BeamNgCommand.UI_BUTTON_PRESSED), "infoui-beamng")


class InfotainmentPlayer(ccomp.ComponentPoller):
    """infotainment component that handles the multiverse -> ui net forwarding and music mixer"""
    stations = glob.glob(str(pathlib.Path(config.RADIO_SOUND_DIR) / r'bensound-*.mp3'))

    session_pid = os.getpid()

    vol_increment = 1 / (2 ** 4)

    vol_range = 2 ** 4

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

    def __init__(self, can_network: CanNetwork, remote_testing=False):
        super().__init__("infoplay", [(config.DIRECTOR_PORT, 'infoplay-commands')], [(config.INFO_PLAY_PORT, 'infoplay-events')])
        self._network = can_network
        self._sidx: int = 0
        self._sound: typ.Union[mixer.Sound, None] = None
        self._sound_enabled = remote_testing

        # Set to True if testing remotely and no audio endpoint is present
        self.remote_testing = False

        # NOTE: start without music/sound
        self._volume = 0.0
        self.system_functionality_level = canlib.FUNCTIONALITY_FULL
        self._set_volume()
        self.play_sound()

    def update_functionality_level(self, new_func_level):
        """
        Updates the component's functionality level
        Unless FUNCTIONALITY_FULL disable all sounds
        """
        self.system_functionality_level = new_func_level
        if self.system_functionality_level != canlib.FUNCTIONALITY_FULL:
            # Disable sound
            self.enable_sound(False)

    def enable_sound(self, enable: bool):
        """
        Disable sound (used in self-driving mode)
        NOTE: maybe use `self._sound.stop()` to interrupt
        current song, so it starts from the beginning when
        sound is re-enabled
        """
        self._sound_enabled = enable
        if enable and (self.system_functionality_level == canlib.FUNCTIONALITY_FULL):
            self.play_sound()
        else:
            if self._sound:
                self._sound.stop()

    def on_start(self):
        self.send_message(ccomp.Message(InfotainmentPlayerStatus.READY), "infoplay-events")

    def on_exit(self):
        if self._sound:
            self._sound.stop()

    def play_sound(self):
        """play sound file depending on station select"""
        if self._sound is not None:
            self._sound.stop()
        if not self.remote_testing:
            mixer.init()
            mixer.get_init()
            self._sound = mixer.Sound(
                str(self.stations[self._sidx])
            )
            self._sound.play(loops=-1)
            self._set_volume()

    def _set_volume(self):
        """find audio session and set the master volume given the volume state"""
        if self.remote_testing:
            pass
        else:
            if self._sound_enabled:
                if self._sound is None:
                    self.play_sound()
                try:
                    session = AudioUtilities.GetProcessSession(self.session_pid)
                    if session:
                        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                        volume.SetMasterVolume(self._volume, None)
                    else:
                        raise RuntimeError(f"audio session doesn't exist!")
                except Exception as exc:
                    info_logger.info(f"Error processing audio session: {exc}")

    @recv_can(canlib.CAN_ID_INFOTAINMENT_STATE, canlib.CAN_FORMAT_INFOTAINMENT_STATE)
    def _(self, data):
        """respond to the infotainment button press"""
        # decode the incoming value
        val = data[0]
        music_playing: bool = (0x1 & val) == 1
        val >>= 1
        station = 0x3 & val
        val >>= 2
        volume = val
        station -= 1
        assert station < 0x3, f"station number isn't valid {station}"

        # apply music mixer actions
        if music_playing:
            target_volume = volume / self.vol_range
            if self._volume != target_volume:
                info_logger.info(f"changing volume to {target_volume} %%")
                self._volume = target_volume
                self._set_volume()
            if self._sidx != station or self._sound is None:
                info_logger.info(f"changing station to {station} index")
                self._sidx = station
                self.play_sound()
        else:
            if self._sound is not None:
                self._sound.stop()
            self._set_volume()

    @recv_can(canlib.CAN_ID_CAR_X, canlib.CAN_FORMAT_CAR_X)
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_X, struct.pack(canlib.CAN_FORMAT_CAR_X, data[0]))

    @recv_can(canlib.CAN_ID_CAR_Y, canlib.CAN_FORMAT_CAR_Y)
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_Y, struct.pack(canlib.CAN_FORMAT_CAR_Y, data[0]))

    @recv_can(canlib.CAN_ID_CAR_Z, canlib.CAN_FORMAT_CAR_Z)
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_Z, struct.pack(canlib.CAN_FORMAT_CAR_Z, data[0]))

    @recv_can(canlib.CAN_ID_CAR_R, canlib.CAN_FORMAT_CAR_R)
    def _(self, data):
        self._network.send(canlib.CAN_ID_CAR_R, struct.pack(canlib.CAN_FORMAT_CAR_R, data[0]))

