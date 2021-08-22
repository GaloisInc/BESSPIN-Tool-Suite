#! /usr/bin/env python3
from besspin.cyberPhys.relaymanager import RelayManager
from besspin.base.utils.misc import *
import besspin.cyberPhys.launch
import besspin.cyberPhys.cyberphyslib.cyberphyslib.demonstrator.component as ccomp
import besspin.cyberPhys.cyberphyslib.cyberphyslib.canlib as canlib

import struct

from can import Message

class Commander(ccomp.ComponentPoller):
    """
    Cyberphys commander
    """
    READY_MSG_TIMEOUT = 10.0 #[s]
    CC_TIMEOUT = 0.1
    POLL_FREQ = 0.5
    DEBUG = True

    # NOTE: this setup is for one commander directing 6 targets
    # For two separate commanders, this has to be adjusted
    targetIds = {
        canlib.TEENSY: 0,
        canlib.TARGET_1: 1,
        canlib.TARGET_2: 2,
        canlib.TARGET_3: 3,
        canlib.TARGET_4: 4,
        canlib.TARGET_5: 5,
        canlib.TARGET_6: 6,
    }

    componentIds = {
        canlib.INFOTAINMENT_SERVER_1: canlib.TARGET_4,
        canlib.INFOTAINMENT_SERVER_2: canlib.TARGET_5,
        canlib.INFOTAINMENT_SERVER_3: canlib.TARGET_6,
        canlib.OTA_UPDATE_SERVER_1: canlib.TARGET_4,
        canlib.OTA_UPDATE_SERVER_2: canlib.TARGET_5,
        canlib.OTA_UPDATE_SERVER_3: canlib.TARGET_6,
        }

    targetList = [k for k in targetIds.keys()]

    def __init__(self):
        # Communication with other components
        name = "commander"
        in_socks, out_socks = besspin.cyberPhys.launch.getComponentPorts(name)
        printAndLog(f"Starting {name} with in_socks: {in_socks} and out_socks: {out_socks}, sample freq: {self.POLL_FREQ}[Hz]", doPrint=False)
        super().__init__(name, in_socks, out_socks, sample_frequency=self.POLL_FREQ)

        # input space as class members
        self.target_reset_requested = False
        self.ready_msg_timeout = False
        self.target_error = False
        self.restart_ok = False
        self.recovery_possible = False
        self.restart_failed = False
        self.degraded_mode_possible = False
        self.targets = ["READY"] * (getSetting('nTargets')+1) # To account for teensy
        self.last_ready_msg = 0.0

        # C&C Network connection
        host, subscribers = besspin.cyberPhys.launch.getNetworkNodes("AdminPc")
        self.cmd_bus = canlib.TcpBus(host, subscribers)

    def on_start(self):
        self.start_poller()

    def on_poll_poll(self, t):
        """main loop"""
        # Check if there is a C&C restart request (single target)
        msg = self.cmd_bus.recv(timeout=self.CC_TIMEOUT)
        if msg:
            cid = msg.arbitration_id
            try:
                if cid == canlib.CAN_ID_CMD_RESTART:
                    devId = struct.unpack(canlib.CAN_FORMAT_CMD_RESTART, msg.data)[0]
                    printAndLog(f"<{self.__class__.__name__}> Reset devId: {devId}", doPrint=Commander.DEBUG)
                    if devId == canlib.TEENSY:
                        self.restartTeensy()
                    elif devId in self.targetIds:
                        self.restartTarget(devId)
                    elif devId in self.componentIds:
                        self.restartComponent(devId)
                elif cid == canlib.CAN_ID_HEARTBEAT_REQ:
                    req_number = struct.unpack(canlib.CAN_FORMAT_HEARTBEAT_REQ, msg.data)[0]
                    print(f"<{self.__class__.__name__}> CAN_ID_HEARTBEAT_REQ: {hex(req_number)}")
                    heartbeat_ack = Message(arbitration_id=canlib.CAN_ID_HEARTBEAT_ACK,
                                            dlc=canlib.CAN_DLC_HEARTBEAT_ACK,
                                            data=struct.pack(canlib.CAN_FORMAT_HEARTBEAT_ACK, canlib.HACKER_KIOSK, req_number))
                    self.cmd_bus.send(heartbeat_ack)
                else:
                    pass
            except Exception as exc:
                printAndLog(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

    def sendComponentError(self, componentId):
        msg = Message(arbitration_id=canlib.CAN_ID_CMD_COMPONENT_ERROR,
                      dlc=canlib.CAN_DLC_CMD_COMPONENT_ERROR,
                      data=struct.pack(canlib.CAN_FORMAT_CMD_COMPONENT_ERROR, componentId, 0))
        printAndLog(f"Commander sending {msg}",doPrint=True)
        self.cmd_bus.send(msg)

    def sendComponentReady(self, componentId):
        msg = Message(arbitration_id=canlib.CAN_ID_CMD_COMPONENT_READY,
                      dlc=canlib.CAN_DLC_CMD_COMPONENT_READY,
                      data=struct.pack(canlib.CAN_FORMAT_CMD_COMPONENT_READY, componentId))
        printAndLog(f"Commander sending {msg}",doPrint=False)
        self.cmd_bus.send(msg)

    def restartTeensy(self):
        """
        Toggle USB connected relays to restart Teensy board
        """
        printAndLog(f"<{self.__class__.__name__}> Restarting Teensy")
        RelayManager.toggleRelays()
        self.sendComponentReady(canlib.TEENSY)
        printAndLog(f"<{self.__class__.__name__}> Teensy restarted")

    def restartTarget(self, devId):
        """
        Restart target
        """
        targetId = self.targetIds[devId]
        printAndLog(f"<{self.__class__.__name__}> Restarting target {targetId}")
        # Logger is disabed inside the resetTarget function
        besspin.target.launch.resetTarget(getSetting('targetObj',targetId=targetId))
        self.sendComponentReady(devId)
        printAndLog(f"<{self.__class__.__name__}> Restarting target {targetId} done")
    
    def restartComponent(self, componentId):
        """
        Restart component
        """
        printAndLog(f"<{self.__class__.__name__}> Restarting component ID {componentId}")

        if componentId == canlib.INFOTAINMENT_SERVER_1 or\
           componentId == canlib.INFOTAINMENT_SERVER_2 or\
           componentId == canlib.INFOTAINMENT_SERVER_3:
            devId = self.componentIds[componentId]
            targetId = self.targetIds[devId]
            printAndLog(f"<{self.__class__.__name__}> Restarting infotainment on target {targetId}")
            # Disable ttyLogger
            wasLogging = besspin.cyberPhys.launch.stopTtyLogging(targetId)
            besspin.cyberPhys.run.resetComponent("infotainment",targetId)
            # Re-enable ttyLogger
            if (wasLogging):
                besspin.cyberPhys.launch.startTtyLogging(targetId)
            self.sendComponentReady(componentId)
            printAndLog(f"<{self.__class__.__name__}> Restarting infotainment done")
        elif componentId == canlib.OTA_UPDATE_SERVER_1 or\
           componentId == canlib.OTA_UPDATE_SERVER_2 or\
           componentId == canlib.OTA_UPDATE_SERVER_3:
            devId = self.componentIds[componentId]
            targetId = self.targetIds[devId]
            printAndLog(f"<{self.__class__.__name__}> Restarting OTA server on target {targetId}")
            # Disable ttyLogger
            wasLogging = besspin.cyberPhys.launch.stopTtyLogging(targetId)
            besspin.cyberPhys.run.resetComponent("ota",targetId)
            # Re-enable ttyLogger
            if (wasLogging):
                besspin.cyberPhys.launch.startTtyLogging(targetId)
            self.sendComponentReady(componentId)
            printAndLog(f"<{self.__class__.__name__}> Restarting OTA server done")
        else:
            printAndLog(f"<{self.__class__.__name__}> Unknown component ID {componentId}")
