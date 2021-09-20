#! /usr/bin/env python3
"""
The main file for the cyberPhys interactive shell
"""

from logging import warn
from besspin.base.utils.misc import *
import besspin.cyberPhys.launch
import besspin.cyberPhys.cyberphyslib.cyberphyslib.demonstrator.component as ccomp
from besspin.cyberPhys.relaymanager import RelayManager

import cmd, threading

@decorate.debugWrap
@decorate.timeWrap
def endInteract(interactor):
    terminator = besspin.cyberPhys.launch.ftQueueUtils("interactiveShell:queue",
        getSetting('interactorQueue'), 'get') #Wait for either the user or the main thread
    print('\r'+ ' '*100,flush=True) #clean the prompt
    if (terminator=='main'): #We have to exit cmdloop()
        interactor.cmdqueue.append("exit\n")
        printAndLog("Please press Enter to continue...")

@decorate.debugWrap
@decorate.timeWrap
def interact():
    interactor = cyberPhysShell()

    # Create a thread that checks endEvent
    endThread = threading.Thread(target=endInteract, args=(interactor,))
    endThread.daemon = True
    getSetting('trash').throwThread(endThread,f"<endInteract> in cyberPhys")
    endThread.start()

    #Start the interactive shell
    interactor.cmdloop()

    #EndInteract (in case the main thread didn't terminate it itself)
    besspin.cyberPhys.launch.ftQueueUtils("interactiveShell:queue", getSetting('interactorQueue'),
        'put', itemToPut='interact')
    endThread.join()

    #Report that it is done
    besspin.cyberPhys.launch.ftQueueUtils("cyberPhysMain:queue", getSetting('cyberPhysQueue'), 'put')


class cyberPhysShell(cmd.Cmd):
    """cyberPhys interactive cmd shell"""

    intro = 'Welcome to cyberPhys interactive cmd shell. Type help or ? to list commands.\n'
    prompt = '(cyberPhys) '

    """ -- Leaving it here if we needed it one day
    def do_help(self,inp):
        if (inp):
            print (getattr(self,f"do_{inp}").__doc__)
        else: #print the commands we want
            commands = [xCmd.split('do_')[-1] for xCmd in dir(self) if xCmd.startswith('do_')]
    """
    def __init__(self):
        super(cyberPhysShell, self).__init__()

    def preloop(self):
        self.name = "interactiveLoop"
        _, out_socks = besspin.cyberPhys.launch.getComponentPorts(self.name)
        self.sender = ccomp.Component(self.name, [], out_socks)
        self.sender.start()
        while not self.sender._ready:
            pass
        printAndLog(f"<{self.__class__.__name__}> Starting.")

    def postloop(self):
        self.sender.stop()
        self.sender.join()
        printAndLog(f"<{self.__class__.__name__}> Terminating.")

    @staticmethod
    def getTargetMember (targetId,memberName):
        xTarget = getSetting('targetObj',targetId=targetId)
        if (hasattr(xTarget,memberName)):
            return getattr(xTarget,memberName)
        else:
            return 'UNKNOWN'

    def precmd(self, line):
        if (line != 'EOF'):
            line = line.lower() #commands are case insensitive
        logging.debug(f"cyberPhys <interactive>: {line}")
        return line

    def do_exit(self,inp):
        """exit
        exits the cyberPhys interactive cmd shell and ends the program"""
        self.sender.send_message(ccomp.Message(f"EXIT"), getSetting('cyberPhysComponentBaseTopic'))
        return True

    def do_quit(self,inp):
        """quit
        quits the cyberPhys interactive cmd shell and ends the program"""
        return self.do_exit(inp)

    def do_EOF(self,inp):
        """exit
        exits the cyberPhys interactive cmd shell and ends the program"""
        print("\n\033[F",flush=True) #make it similar to quit/exit
        return True

    def emptyline(self): #to avoid repeating the last command on <enter>
        return

    def do_ip(self,inp):
        """ip
        Displays the IPs of the running targets"""
        for iTarget in range(1,getSetting('nTargets')+1):
            printAndLog(f"<target{iTarget}>: {self.getTargetMember(iTarget,'ipTarget')}")
        return

    def do_restart_teensy(self,inp):
        """
        Restart Teensy board
        """
        printAndLog("Restarting Teensy")
        RelayManager.toggleRelays()
        printAndLog("Teensy restarted")

    def do_uart(self,inp):
        """uart
        Displays the ports to which the UART/TTY is piped for the running targets"""
        printAndLog("You may access the UART using: <socat - TCP4:localhost:${port}> or <nc localhost ${port}>.")
        for iTarget in range(1,getSetting('nTargets')+1):
            if (isEnabled('isUartPiped',targetId=iTarget)):
                printAndLog(f"<target{iTarget}>: {getSetting('uartPipePort',targetId=iTarget)}")
            else:
                printAndLog(f"<target{iTarget}>: UART not piped. Use <pipe {iTarget}> to start piping it.")
        return

    def do_info(self,inp):
        """info
        Displays info about the running targets"""
        for iTarget in range(1,getSetting('nTargets')+1):
            printAndLog(f"<target{iTarget}>:")
            for xInfo in ['target', 'processor', 'osImage']:
                printAndLog(f"\t{xInfo} = {self.getTargetMember(iTarget,xInfo)}")
        return

    def do_pipe(self,inp):
        """pipe [start|stop] TARGET_ID
        starts|stops piping the target with the chosen ID"""
        items = inp.split(' ')
        if (len(items)>2):
            print(self.do_pipe.__doc__)
            return
        if (len(items)==1):
            action, targetId = ['start', items[0]]
        else:
            action, targetId = items

        try:
            assert (action in ['start', 'stop']), "validating piping action"
            assert (int(targetId) in range(1,getSetting('nTargets')+1)), "validating target ID"
            targetId = int(targetId)
        except Exception as exc:
            warnAndLog("Error in using pipe", exc=exc, doPrint=False)
            print(self.do_pipe.__doc__)
            return
        if (action == 'start'):
            besspin.cyberPhys.launch.stopTtyLogging(targetId)
            besspin.cyberPhys.launch.startUartPiping(targetId)
        else:
            besspin.cyberPhys.launch.endUartPiping(targetId, doPrintWarning=True)
            besspin.cyberPhys.launch.startTtyLogging(targetId)
