#! /usr/bin/env python3

from besspin.base.utils.misc import *
import besspin.cyberPhys.launch
from besspin.base.threadControl import ftQueueUtils
import besspin.cyberPhys.cyberphyslib.cyberphyslib.demonstrator.component as ccomp

import struct
import ipaddress

class Watchdog(ccomp.ComponentPoller):
    """
    This function keeps monitoring the target, and if it goes down, it resets it
    " There are 3 things that we need to make sure while developing this:
    " 1. Can watch
    " 2. resets
    " 3. Is able to exit

    During each poll, this watchdog has to:
    1. check if isTargetAlive()
      - if not, attempt to reset the target
    2. see when the last hearbeat was received
    3. reeset the target upon request
    """
    def __init__(self, targetId):
        in_socks, out_socks = besspin.cyberPhys.launch.getComponentPorts('watchdogBase')
        name = f"watchdog{targetId}"
        f_Hz = getSetting('cyberPhysWatchdogFrequency')
        super().__init__(name, in_socks, out_socks, sample_frequency=f_Hz)

        self.wHeartbeatQueue = getSetting('watchdogHeartbeatQueue', targetId=targetId)
        self.last_heartbeat = 0
        self.targetId = targetId
        self.targetIp = besspin.cyberPhys.launch.get_target_ip(targetId)
    
    def on_poll_poll(self, t):
        """watchdog mainloop"""
        self.process_hearbeat()
        if not besspin.cyberPhys.run.watchdog.isTargetAlive(self.targetId):
            printAndLog(f"<{self.name}> Target is not alive, stoping")
            self.stop()

    def process_hearbeat(self) -> bool:
        responses = []
        while not self.wHeartbeatQueue.empty():
            responses.append(ftQueueUtils(f"watchDogHeartbeatQueue{self.targetId}",self.wHeartbeatQueue,'get'))

        try:
            msgs = [msg for msg in responses if str(ipaddress.IPv4Address(struct.unpack('<I', msg.data[0:4])[0])) == self.targetIp]
            if msgs:
                msg = msgs[0]
                printAndLog(f"<target{self.targetId}>: Heartbeat received, {msg.timestamp}s, \
                    reqID: {int.from_bytes(msg.data[4:8],'big')}",doPrint=False)
                return True
            else:
                warnAndLog(f"<target{self.targetId}>: Heartbeat missed",doPrint=False)
                # TODO: do something more here
                return False
        except Exception as exc:
            warnAndLog(f"<target{self.targetId}> Exception occured processing hearbeat response: {exc}") 
            return False

    def reset_target(self, errorString: str):
        """Reset target and return true if the reset was successful"""
        warnAndLog(f"<target{self.targetId}>: {errorString}! Resetting...")
        # Here we should reset
        besspin.target.launch.resetTarget(getSetting('targetObj',targetId=self.targetId))
        printAndLog("Please press Enter to return to the interactive shell...")

    @recv_topic("base-topic")
    def _(self, msg, t):
        """Filter received messages"""
        if msg == f"RESET {self.targetId}":
            self.reset_target("Reset requested")



