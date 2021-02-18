#! /usr/bin/env python3
""" 
The main file to start launching cyberPhys
"""

from fett.base.utils.misc import *
import fett.target.launch
import fett.cyberPhys.interactive
import fett.cyberPhys.run
import fett.cyberPhys.canlib
from fett.base.threadControl import ftQueueUtils
import threading, queue, pexpect

# Import for CAN bus
import struct
import socket
import select
import time
from can import BusABC, Message

@decorate.debugWrap
@decorate.timeWrap
def startCyberPhys():
    printAndLog (f"Launching FETT <cyberPhys mode>...")
    # start/prepareEnv/Launch
    runThreadPerTarget(fett.target.launch.startFett)
    printAndLog (f"FETT <cyberPhys mode> is launched!")

    if (isEnabled('interactiveShell')):
        # - We need a way for communication between this (main thread) and the watchdog threads [and interacting thread].
        # - We'll use queues. Each queue should be used in one-way communication. So there is a main queue that is watched here.
        # - And we create a queue for each watchdog [and interacting thread] (Creating a threading.Event() is possible, but not
        #   for interactive, so we'll keep it all as queues for consistency and more future compatibility).
        exitQueue = queue.Queue(maxsize=getSetting('nTargets')+int(isEnabled('interactiveShell')))
        setSetting('cyberPhysQueue',exitQueue)
        for targetId in range(1,getSetting('nTargets')+1):
            setSetting('watchdogQueue',queue.Queue(maxsize=1),targetId=targetId)

        # Start the watchdogs
        allThreads = runThreadPerTarget(fett.cyberPhys.run.watchdog,onlyStart=True)

        # Pipe the UART
        if (isEnabled('pipeTheUart')):
            runThreadPerTarget(startUartPiping)
            printAndLog("You may access the UART using: <socat - TCP4:localhost:${port}> or <nc localhost ${port}>.")
        else: #log the output instead
            runThreadPerTarget(startTtyLogging)

        # Create an interactor queue
        # Interactor can be terminated because of a watchdog reported error, or by the user
        setSetting('interactorQueue',queue.Queue(maxsize=2))

        # Start the interactive shell
        allThreads += runThreadPerTarget(fett.cyberPhys.interactive.interact,
                        addTargetIdToKwargs=False, onlyStart=True, singleThread=True)

        # Start the watch on the watchdogs [+ interactive shell]
        ftQueueUtils("cyberPhysMain:queue",exitQueue,'get') #block until receiving an error or termination

        # Start the heartbeat watchdog
        allThreads += runThreadPerTarget(heartBeatWatchDog,
                        addTargetIdToKwargs=False, onlyStart=True, singleThread=True)
    
        # Terminating all threads
        for targetId in range(1,getSetting('nTargets')+1):
            ftQueueUtils(f"target{targetId}:watchdog:queue",getSetting('watchdogQueue',targetId=targetId),'put')
        if (isEnabled('interactiveShell')):
            ftQueueUtils("interactiveShell:queue",getSetting('interactorQueue'),'put',itemToPut='main')

        # TODO: Create a listener thread that reads CAN messages from a socket

        # Waiting for all threads to terminate
        for xThread in allThreads:
            xThread.join()

    return

@decorate.debugWrap
@decorate.timeWrap
def endCyberPhys():
    printAndLog (f"Terminating FETT...")
    if (isEnabled('interactiveShell')):
        # End piping and logging
        runThreadPerTarget(endUartPiping)
        runThreadPerTarget(stopTtyLogging)
    # Terminate the targets
    runThreadPerTarget(fett.target.launch.endFett,
                    mapTargetSettingsToKwargs=[('xTarget','targetObj')],
                    addTargetIdToKwargs=False)

@decorate.debugWrap
@decorate.timeWrap
def runThreadPerTarget(func, tArgs=(), tKwargs=None, addTargetIdToKwargs=True, 
        mapTargetSettingsToKwargs=[], onlyStart=False, singleThread=False):
    """
    This function starts a thread for each target in cyberPhys mode
    func: A handle to the function of the thread.
    tArgs: The tuples of args with which the thread function is to be called
    tKwargs: The dictionary of kwargs with which the thread function is to be called.
            (Note that it has to be initialized to None because of how functions in 
            python are defined as first class objects)
    addTargetIdToKwargs: If enabled, kwargs will have "targetId=${iTarget}" for iTarget in [1,..,nTargets]
    mapTargetSettingsToKwargs: A list of tuples (xKwargName, xSettingName), for each tuple, kwarfs will be
                                augmented with "xKwargName=_settings[${iTarget}][xSettingName]"
    onlyStart: If enabled, it will just launch the threads without waiting for them to finish.
    singleThread: If enabled, instead of a thread per target, only a single thread is created
    """
    xThreads = []
    if (tKwargs is None):
        tKwargs = {}
    if (singleThread):
        allTargets = range(1)
    else:
        allTargets = range(1,getSetting('nTargets')+1)
    for iTarget in allTargets:
        if (addTargetIdToKwargs):
            tKwargs['targetId'] = iTarget
        for kwargName,xSetting in mapTargetSettingsToKwargs:
            tKwargs[kwargName] = getSetting(xSetting,targetId=iTarget)
        xThread = threading.Thread(target=func, args=tArgs, kwargs=tKwargs)
        xThread.daemon = True
        getSetting('trash').throwThread(xThread,f"<{func.__name__}> for target{iTarget}")
        xThread.start()
        xThreads.append(xThread)

    if (not onlyStart):
        for xThread in xThreads:
            xThread.join()

    return xThreads

@decorate.debugWrap
def startUartPiping(targetId):
    xTarget = getSetting('targetObj',targetId=targetId)
    if (isEnabled('isUartPiped',targetId=targetId)):
        warnAndLog(f"{xTarget.targetIdInfo}startUartPiping: the UART is already piped to port <{getSetting('uartPipePort',targetId=targetId)}>.")
        return
    if (isEnabled('isTtyLogging',targetId=targetId)):
        warnAndLog(f"{xTarget.targetIdInfo}startUartPiping: Has to turn off tty logging first.")
        stopTtyLogging(targetId)
    uartPipePort = xTarget.findPort(portUse='uartFwdPort')
    setSetting('uartPipePort',uartPipePort,targetId=targetId)
    try:
        xTarget.uartSocatProc = subprocess.Popen(
            ['socat', 'STDIO,ignoreeof', f"TCP-LISTEN:{uartPipePort},reuseaddr,fork,max-children=1"],
            stdout=xTarget.process.child_fd,stdin=xTarget.process.child_fd,stderr=xTarget.process.child_fd)
    except Exception as exc:
        xTarget.terminateAndExit(f"{xTarget.targetIdInfo}startUartPiping: Failed to start the piping.",
            exc=exc,exitCode=EXIT.Run)
    setSetting('isUartPiped',True,targetId=targetId)
    printAndLog (f"{xTarget.targetIdInfo}UART is piped to port <{uartPipePort}>.")

@decorate.debugWrap
def endUartPiping(targetId, doPrintWarning=False):
    xTarget = getSetting('targetObj',targetId=targetId)
    if (not isEnabled('isUartPiped',targetId=targetId)):
        warnAndLog(f"{xTarget.targetIdInfo}endUartPiping: The UART is not piped!",doPrint=doPrintWarning)
        return #The function gets called in case the uart was piped in the interactive mode
    try:
        xTarget.uartSocatProc.kill() # No need for fancier ways as we use Popen with shell=False
    except Exception as exc:
        warnAndLog(f"{xTarget.targetIdInfo}endUartPiping: Failed to kill the process.",exc=exc)
    setSetting('isUartPiped',False,targetId=targetId)


class TtyLogger(threading.Thread):
    def __init__(self, xTarget):
        self.xTarget = xTarget
        self.process = xTarget.process
        self.stopLogging = threading.Event()
        self.finishedLogging = threading.Event()
        threading.Thread.__init__(self)
        self.daemon = True
        getSetting('trash').throwThread(self,f"<TtyLogger> for target{xTarget.targetId}")

    def run(self):
        while (not self.stopLogging.is_set()):
            try:
                fetchedBytes = self.process.read_nonblocking(size=1024,timeout=1) #size is arbitrary; it wouldn't matter much
                textBack = str(fetchedBytes,'utf-8')
            except pexpect.TIMEOUT:
                continue
            except Exception as exc:
                warnAndLog(f"{self.xTarget.targetIdInfo}TtyLogger: Failed to read from target! Logging will stop.",exc=exc)
                break
        self.finishedLogging.set()

    def stop(self):
        self.stopLogging.set()
        self.finishedLogging.wait() #This to ensure not to return before the `read` times out

@decorate.debugWrap
def startTtyLogging(targetId):
    xTarget = getSetting('targetObj',targetId=targetId)
    if (isEnabled('isTtyLogging',targetId=targetId)):
        warnAndLog(f"{xTarget.targetIdInfo}startTtyLogging: the TTY is already being logged.")
        return
    if (isEnabled('isUartPiped',targetId=targetId)):
        warnAndLog(f"{xTarget.targetIdInfo}startTtyLogging: Has to turn off uart piping first.")
        endUartPiping(targetId)
    ttyLogger = TtyLogger(xTarget)
    setSetting('ttyLogger',ttyLogger,targetId=targetId)
    ttyLogger.start()
    setSetting('isTtyLogging',True,targetId=targetId)

@decorate.debugWrap
def stopTtyLogging(targetId):
    if (not isEnabled('isTtyLogging',targetId=targetId)):
        warnAndLog(f"{xTarget.targetIdInfo}stopTtyLogging: The TTY was not being logged!",doPrint=False)
        return
    getSetting('ttyLogger',targetId=targetId).stop()
    setSetting('isTtyLogging',False,targetId=targetId)

class UDPBus(BusABC):
    """
    Enable basic communication over UDP

    The bus is bound to a particular ADDR and PORT upon creation,
    and can receive data only from that addr/port.

    The bus can send data to any address/port.
    """
    CAN_MIN_BYTES = 4 + 1 + 1  # sending an empty frame doesn't make sense, min 6 bytes per frame
    CAN_MAX_BYTES = 64 + 4 + 1  # 64 bytes of DATA, 4 bytes of ID, 1 byte od DLC

    def __init__(self, bind_ip, bind_port):
        super(UDPBus, self).__init__(channel="dummy")
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.bind((bind_ip, bind_port))

    def send(self, msg, tx_ip, tx_port, timeout=None):
        a_id = struct.pack('<I', msg.arbitration_id)
        byte_msg = bytearray(a_id)
        byte_msg.append(msg.dlc)
        byte_msg += bytearray([msg.data[i] for i in range(0, msg.dlc)])
        if timeout:
            print("Warning: ignoring timeout {}".format(timeout))
        self._sock.sendto(byte_msg, (tx_ip, tx_port))

    def _recv_internal(self, timeout):
        ready = select.select([self._sock], [], [], timeout)
        if ready[0]:
            rx_data, sender_addr = self._sock.recvfrom(UDPBus.CAN_MAX_BYTES)
            print("Info: received {} bytes from {}".format(len(rx_data), sender_addr))
            if len(rx_data) < UDPBus.CAN_MIN_BYTES:
                print("Warning: received only {} bytes, ignoring.".format(len(rx_data)))
            else:
                s = bytearray(rx_data[0:4])
                arb_id = struct.unpack('<I', s)[0]
                dlc = rx_data[4]
                if dlc == len(rx_data[5:]):
                    data = rx_data[5:]
                    msg = Message(timestamp=time.time(),
                                arbitration_id=arb_id,
                                dlc=dlc,
                                data=data)
                    return msg, False
                else:
                    print("Warning: DLC ({}) and the length of data ({}) don't match, ignoring.".format(dlc,len(rx_data)))
        return None, False

@decorate.debugWrap
@decorate.timeWrap
def heartBeatWatchDog():
    """
    Sends heartbeat requests and listens to responses.
    """
    canbus = UDPBus(getSetting('vcu118IpHost'),getSetting('cyberPhysCanbusPort'))
    canbus.set_filters([{"can_id": canlib.CAN_ID_HEARTBEAT_ACK, "can_mask": 0XFFFFFFFF, "extended": True}])
    cnt = 0

    while(True):
        cnt += 1
        heartbeat_req = Message(arbitration_id=canlib.CAN_ID_HEARTBEAT_REQ,
                                    is_extended_id=True,
                                    data=[cnt.to_bytes(4, byteorder = 'big')])
        canbus.send(heartbeat_req, getSetting('vcu118BroadcastIp'),getSetting('cyberPhysCanbusPort'))
        printAndLog (f"FETT <heartBeatWatchDog mode> sending message")

        # Assume one second window to receive watchdog responses
        endOfWait = time.time() + 1.0
        responses = []
        while (time.time() < endOfWait) and (len(responses) < getSetting('nTargets')):
            heartbeat_ack = canbus.recv(timeout=0.1)
            print(f"RX: {heartbeat_ack}")
            responses.append(heartbeat_ack)
        printAndLog("Got {len(responses)} acks")
