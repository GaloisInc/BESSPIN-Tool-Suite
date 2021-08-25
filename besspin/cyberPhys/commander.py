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
    CC_TIMEOUT = 0.1
    POLL_FREQ = 10
    DEBUG = True

    componentIds = {
        # Services and their corresponding targets
        canlib.INFOTAINMENT_SERVER_1: canlib.DEBIAN_1,
        canlib.INFOTAINMENT_SERVER_2: canlib.DEBIAN_2_LMCO,
        canlib.INFOTAINMENT_SERVER_3: canlib.DEBIAN_3,
        canlib.OTA_UPDATE_SERVER_1: canlib.DEBIAN_1,
        canlib.OTA_UPDATE_SERVER_2: canlib.DEBIAN_2_LMCO,
        canlib.OTA_UPDATE_SERVER_3: canlib.DEBIAN_3,
        }

    def generateTargetList(self):
        """
        Generate list of targets and their IDs based on the custom
        target names. We get a mapping from Calib_IDs to targetIds
        """
        for targetId in range(1,getSetting('nTargets')+1):
            targetName = getSetting("customTargetName",targetId=targetId)
            self.targetIds[canlib.CanlibComponentIds[targetName]] = targetId

    def __init__(self):
        # Communication with other components
        name = "commander"
        in_socks, out_socks = besspin.cyberPhys.launch.getComponentPorts(name)
        printAndLog(f"Starting {name} with in_socks: {in_socks} and out_socks: {out_socks}, sample freq: {self.POLL_FREQ}[Hz]", doPrint=Commander.DEBUG)
        super().__init__(name, in_socks, out_socks, sample_frequency=self.POLL_FREQ)

        self.targetIds = {}
        self.generateTargetList()

        # C&C Network connection
        self.hostname = getSetting('hostName')
        printAndLog(f"<{self.__class__.__name__}> Hostname: {self.hostname}", doPrint=Commander.DEBUG)
        host, subscribers = besspin.cyberPhys.launch.getNetworkNodes(self.hostname)
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
                    if devId == canlib.TEENSY:
                        # Teensy is connected to NUC_1
                        if self.hostname == "AdminPc":
                            self.restartTeensy()
                    elif devId in self.targetIds:
                        self.restartTarget(devId)
                    elif devId in self.componentIds:
                        self.restartComponent(devId)
                elif cid == canlib.CAN_ID_HEARTBEAT_REQ:
                    req_number = struct.unpack(canlib.CAN_FORMAT_HEARTBEAT_REQ, msg.data)[0]
                    print(f"<{self.__class__.__name__}> CAN_ID_HEARTBEAT_REQ: {hex(req_number)}")
                    if self.hostname == "AdminPC":
                        tool_suite_id = canlib.BESSPIN_TOOL_FREERTOS
                    else:
                        tool_suite_id = canlib.BESSPIN_TOOL_DEBIAN
                    heartbeat_ack = Message(arbitration_id=canlib.CAN_ID_HEARTBEAT_ACK,
                                            dlc=canlib.CAN_DLC_HEARTBEAT_ACK,
                                            data=struct.pack(canlib.CAN_FORMAT_HEARTBEAT_ACK, tool_suite_id, req_number))
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
        # On which target does the component run?
        devId = self.componentIds[componentId]
        # Do we have such target?
        targetId = self.targetIds.get(devId,None)
        if targetId:
            componentName = canlib.CanlibComponentNames[componentId]
            targetName = canlib.CanlibComponentNames[devId]
            printAndLog(f"<{self.__class__.__name__}> Restarting {componentName} on target {targetId} ({targetName}")
            # Disable ttyLogger
            wasLogging = besspin.cyberPhys.launch.stopTtyLogging(targetId)

            if componentId == canlib.INFOTAINMENT_SERVER_1 or componentId == canlib.INFOTAINMENT_SERVER_2 or componentId == canlib.INFOTAINMENT_SERVER_3:
                besspin.cyberPhys.run.resetComponent("infotainment",targetId)
            elif componentId == canlib.OTA_UPDATE_SERVER_1 or componentId == canlib.OTA_UPDATE_SERVER_2 or componentId == canlib.OTA_UPDATE_SERVER_3:
                besspin.cyberPhys.run.resetComponent("ota",targetId)
            # Re-enable ttyLogger
            if (wasLogging):
                besspin.cyberPhys.launch.startTtyLogging(targetId)
            self.sendComponentReady(componentId)
            printAndLog(f"<{self.__class__.__name__}> Restarting {componentName} done")
        else:
            pass
