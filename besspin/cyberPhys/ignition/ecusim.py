"""
Project: SSITH CyberPhysical Demonstrator
Name: ecusim.py
Author: Ethan Lew <elew@galois.com>
Date: 19 October 2020

usage: ecusim.py [-h] [-stub STUB] [-latency LATENCY]

ECU Prototype with Peripheral Stubs

optional arguments:
  -h, --help        show this help message and exit
  -stub STUB        String ID of Stub
  -latency LATENCY  Simulated Latency (in ms)

P1 Emulation

    Prototype of the interface for the P1 module. The IO is:
        1. send vehicle control data [steering, throttle, brake, and gear]
        2. accept can packets of BeamNG data
        3. read stub peripherals for gear, throttle, and brake
"""
from cyberphyslib.demonstrator import can, config, component
from cyberphyslib.canlib import canspecs
import struct
import time
import pygame
import enum


class T150Axes(enum.IntEnum):
    """axis indicies for T150 Thrustmaster"""
    STEERING_WHEEL = 0
    BRAKE = 1
    THROTTLE = 2


# thrustmaster T150 name
T150_NAME = 'Thrustmaster T150 Racing Wheel'


def init_t150() -> pygame.joystick.Joystick:
    pygame.init()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    tm_joy = None

    for joy in joysticks:
        joy.init()
        if joy.get_name() == T150_NAME:
            if tm_joy is None:
                tm_joy = joy
            else:
                raise RuntimeError(f"More than one racing wheel '{T150_NAME}' is connected!")

    if tm_joy is None:
        raise RuntimeError(f"No racing wheel '{T150_NAME}' is connected!")
    return tm_joy


def joy_info(joy: pygame.joystick.Joystick) -> str:
    """information string of a joystick object"""
    ostr = joy.get_name()
    ostr += '\t\n' +  f"Number of trackballs: {joy.get_numballs()}"
    ostr += '\t\n' + f"Number of buttons: {joy.get_numbuttons()}"
    ostr += '\t\n' + f"Number of axes: {joy.get_numaxes()}"
    ostr += '\t\n' + f"Number of hats: {joy.get_numhats()}"
    return ostr


def isclose(a: float, b: float, rel_tol=1e-09, abs_tol=0.0) -> bool:
    """float comparison -- is close"""
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


# models the CAN UDP facilities available on the ECU
net = can.CanUdpNetwork("ecusim", config.CAN_PORT, config.SIM_IP)
cid = None
pkt = None


class ECUPrototypeBase(component.ComponentPoller):
    """
    Base Class for ECU Prototype -- implement recv and on_poll methods for action/reaction
    """
    packet_out_descr = {"steer": canspecs.CAN_ID_STEERING_INPUT,
                        "throttle": canspecs.CAN_ID_THROTTLE_INPUT,
                        "brake": canspecs.CAN_ID_BRAKE_INPUT,
                        "gear": canspecs.CAN_ID_GEAR}
    packet_in_descr = {}

    @staticmethod
    def send_control(id, fmt, val, bounds = (0.0, 1.0), mult=100.0):
        global pkt, cid
        val = int(mult * min(max(val, bounds[0]), bounds[1]))
        cid = id
        pkt = struct.pack(fmt, val)
        return net.send(id, struct.pack(fmt, val))

    @staticmethod
    def steer(val):
        return ECUPrototypeBase.send_control(ECUPrototypeBase.packet_out_descr["steer"], "!b", val, bounds=(-1.0, 1.0))

    @staticmethod
    def throttle(val):
        return ECUPrototypeBase.send_control(ECUPrototypeBase.packet_out_descr["throttle"], "!B", val, bounds=(0.0, 1.0))

    @staticmethod
    def brake(val):
        return ECUPrototypeBase.send_control(ECUPrototypeBase.packet_out_descr["brake"], "!B", val, bounds=(0.0, 1.0))

    @staticmethod
    def gear(val):
        return ECUPrototypeBase.send_control(ECUPrototypeBase.packet_out_descr["gear"], "!c", val, bounds=(-1, 5))

    def __init__(self, *args, latency = 20E-3, **kwargs):
        super().__init__(*args, **kwargs)
        self.latency = latency

    def on_start(self) -> None:
        self.start_poller()

    def on_exit(self) -> None:
        self.stop_poller()

    def on_poll_poll(self, t) -> None:
        raise NotImplementedError

    def recv(self, id, data_len, data):
        """implement this to respond to sensor data"""
        pass

    @property
    def fields_in(self):
        return tuple(self.packet_in_descr.keys())

    @property
    def fields_out(self):
        return tuple(self.packet_out_descr.keys())

    @property
    def ids_fields(self):
        return dict((a[::-1] for a in self.packet_in_descr.items()))


class ECUPrototypeT150(ECUPrototypeBase):
    """use Thrustmaster T150 steering wheel for peripheral values"""
    def on_poll_start(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(size=(600, 300))
        pygame.display.set_caption('ECU Sim')

        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
        self.tm_joy = init_t150()
        self.steer_val = None
        self.throttle_val = None
        self.brake_val = None

    def on_poll_poll(self, t) -> None:
        self.screen.fill((255, 255, 255))
        if cid is not None and pkt is not None:
            out_str = f"Sending CAN ID: {cid}"
            out_str  += f", Data: {pkt.hex()}" if pkt is not None else ""
            text_surface = self.font.render(out_str, True, (0, 0, 0))
            self.screen.blit(text_surface, dest=(0, 0))
        pygame.display.update()

        events = pygame.event.get()
        if len(events) > 0:
            event = events[-1]
            if event.type == pygame.QUIT:
                pygame.quit()  # sys.exit() if sys is imported
                self.stop_poller()
                return

        # add latency for ADC read, network latency
        time.sleep(self.latency)

        new_steer = self.tm_joy.get_axis(T150Axes.STEERING_WHEEL)
        if self.steer_val is None or not isclose(self.steer_val, new_steer, rel_tol=1E-03):
            self.steer(new_steer)
            self.steer_val = new_steer

        new_brake = -self.tm_joy.get_axis(T150Axes.BRAKE)
        if self.brake_val is None or not isclose(self.brake_val, new_brake, rel_tol=1E-03):
            self.brake(100 * new_brake)
            self.brake_val = new_brake

        new_throttle = -self.tm_joy.get_axis(T150Axes.THROTTLE)
        if self.throttle_val is None or not isclose(self.throttle_val, new_throttle, rel_tol=1E-03):
            self.throttle(100 * new_throttle)
            self.throttle_val = new_throttle


class ECUPrototypeKeyboard(ECUPrototypeBase):
    """use keyboard arrow keys for peripheral values"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_poll_start(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(size=(600, 300))
        pygame.display.set_caption('ECU Sim')
        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)

    def on_poll_poll(self, t) -> None:
        self.screen.fill((255, 255, 255))
        if cid is not None:
            out_str = f"Sending CAN ID: {cid}"
            out_str  += f", Data: {pkt.hex()}" if pkt is not None else ""
            text_surface = self.font.render(out_str, True, (0, 0, 0))
            self.screen.blit(text_surface, dest=(0, 0))
        pygame.display.update()

        events = pygame.event.get()
        if len(events) > 0:
            event = events[-1]
            if event.type == pygame.QUIT:
                pygame.quit()  # sys.exit() if sys is imported
            if event.type == pygame.KEYDOWN:
                # TODO: change to gear up/down
                if event.key == pygame.K_DOWN:
                    self.brake(1.0)
                if event.key == pygame.K_UP:
                    self.throttle(1.0)
                if event.key == pygame.K_LEFT:
                    self.steer(-1.0)
                if event.key == pygame.K_RIGHT:
                    self.steer(1.0)
            else:
                self.brake(0.0)
                self.throttle(0.0)
                self.steer(0.0)

        time.sleep(self.latency)


if __name__ == "__main__":
    import argparse

    stub_names = ["keyboard", "thrustmaster"]

    def stub_str(x: str) -> str:
        assert x in stub_names, f"passed stub ID must be in {stub_names}"
        return x

    parser = argparse.ArgumentParser(description="ECU Prototype with Peripheral Stubs")
    parser.add_argument("-stub", type=stub_str, default='thrustmaster', help="String ID of Stub")
    parser.add_argument("-latency", type=int, default=20, help="Simulated Latency (in ms)")
    args = parser.parse_args()

    listeners_cls = {"keyboard" : ECUPrototypeKeyboard, "thrustmaster": ECUPrototypeT150}
    listener = listeners_cls[args.stub]("ecu-sim", [], [], latency = args.latency * 1E-3)
    net.register(listener)
    net.start()
    listener.start()
    while True:
        time.sleep(1.0)