"""
Project: SSITH CyberPhysical Demonstrator
Name: infosim.py
Author: Ethan Lew <elew@galois.com>
Date: 21 January 2021

Infotainment Server Prototype with Keyboard Stub
"""
from canlib import canspecs
from demonstrator import can, config, component
import struct
import time
import pygame


net = can.CanUdpNetwork("infosim", config.INFO_UI_PORT, "127.0.0.1")
cid = None
pkt = None


class InfoPrototypeBase(component.ComponentPoller):
    n_stations =  3

    @staticmethod
    def send_button_press(val: int):
        global cid, pkt
        cid = canspecs.CAN_ID_BUTTON_PRESSED
        pkt = struct.pack("i", val)
        return net.send(cid, pkt)

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


class InfoPrototypeKeyboard(InfoPrototypeBase):
    """use keyboard arrow keys for peripheral values

    KEY_LEFT, KEY_RIGHT: station previous, next
    KEY_DOWN, KEY_UP: volume down, up
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # keep internal state as station is relative for keyboard prototype
        self._station = 0

    def on_poll_start(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode(size=(600, 300))
        pygame.display.set_caption('Infotainment Sim')
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
                self.stop()
            if event.type == pygame.KEYDOWN:
                # TODO: change to gear up/down
                if event.key == pygame.K_DOWN:
                    self.send_button_press(0x10)
                if event.key == pygame.K_UP:
                    self.send_button_press(0x11)
                if event.key == pygame.K_LEFT:
                    self._station += 1
                    self._station %= self.n_stations
                    self.send_button_press(self._station + 1)
                if event.key == pygame.K_RIGHT:
                    self._station -= 1
                    self._station %= self.n_stations
                    self.send_button_press(self._station + 1)
        time.sleep(self.latency)


# start the keyboard (only available) prototype
info_proto = InfoPrototypeKeyboard("info-sim", [], [])
info_proto.start()
while not info_proto.stopped:
    time.sleep(0.1)
