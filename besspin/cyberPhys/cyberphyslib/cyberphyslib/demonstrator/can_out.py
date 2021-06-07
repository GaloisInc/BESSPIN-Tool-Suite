
from .component import ComponentPoller
from .can import CanMultiverse
import cyberphyslib.demonstrator.config as config
import cyberphyslib.canlib.canspecs as canspecs
import cyberphyslib.demonstrator.message as cmesg

import struct
import math
import enum

from .logger import can_logger


class CanOutStatus(enum.IntEnum):
    READY = enum.auto()
    ERROR = enum.auto()


class CanOutPoller(ComponentPoller):

    """Polls vehicle location and broadcasts it via CAN at 10hz"""
    def __init__(self, network : CanMultiverse):
        super().__init__("location", [config.BEAMNG_COMPONENT_VEHICLE, (config.DIRECTOR_PORT, "location-commands")],
                         [(config.LOCATION_PORT, "location-events")],
                         sample_frequency=config.LOCATION_POLL_HZ)
        self._location = None
        self._last_location = None
        self._network = network
    
    def on_start(self) -> None:
        can_logger.debug("Starting CanOutPoller Component")
        if not self.stopped:
            self.start_poller()
        self.send_message(cmesg.Message(CanOutStatus.READY), "location-events")

    def on_poll_poll(self, t):
        """Get current vehicle location"""
        super().on_poll_poll(t)
        if self._location is not None:
            pos = self._location[0]

            # Send position X, Y, Z
            if self._last_location is not None:
                last_pos = self._last_location[0]
                send_x, send_y, send_z = [abs(lpi - pi) > config.MIN_POSITION_CHANGE for lpi, pi in zip(last_pos, pos)]
            else:
                send_x, send_y, send_z = (True, True, True)

            if send_x:
                self._network.send(canspecs.CAN_ID_CAR_X, struct.pack("!f", pos[0]))
            if send_y:
                self._network.send(canspecs.CAN_ID_CAR_Y, struct.pack("!f", pos[1]))
            if send_z:
                self._network.send(canspecs.CAN_ID_CAR_Z, struct.pack("!f", pos[2]))

            heading = self.compute_heading(self._location)
            if self._last_location is not None:
                last_heading = self.compute_heading(self._last_location)
                send_heading = abs(last_heading - heading) > config.MIN_HEADING_CHANGE
            else:
                send_heading = True

            # Send direction (heading)
            if send_heading:
                self._network.send(canspecs.CAN_ID_CAR_R, struct.pack("!f", heading))

            # save the location
            self._last_location = self._location

    def compute_heading(self, location):
        """Convert unit circle coordinates in location data to a heading"""
        x = location[1][0]
        y = location[1][1]
        heading = math.degrees(math.atan2(x,y))
        if x < 0:
            heading = heading + 360
        return heading

    @recv_topic("beamng-vehicle")
    def _(self, msg, t):
        """Subscribe to sim service sensor electrics"""
        self._location = msg.message

    def on_exit(self) -> None:
        self.stop_poller()        
