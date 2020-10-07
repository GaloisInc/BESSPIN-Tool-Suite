#! /usr/bin/env python3
""" 
The main file for the cyberPhys interactive shell
"""

from fett.base.utils.misc import *
import cmd, os

@decorate.debugWrap
@decorate.timeWrap
def interact():
    interactor = cyberPhysShell()
    interactor.cmdloop()

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
        return True

    def do_quit(self,inp):
        """quit
        quits the cyberPhys interactive cmd shell and ends the program"""
        return True

    def do_EOF(self,inp):
        """exit
        exits the cyberPhys interactive cmd shell and ends the program"""
        return True

    def emptyline(self): #to avoid repeating the last command on <enter>
        return

    def do_ip(self,inp):
        """ip
        Displays the IPs of the running targets"""
        for iTarget in range(1,getSetting('nTargets')+1):
            printAndLog(f"<target{iTarget}>: {self.getTargetMember(iTarget,'ipTarget')}")
        return

    def do_uart(self,inp):
        """uart
        Displays the ports to which the UART/TTY is piped for the running targets"""
        printAndLog("You may access the UART using: <socat - TCP4:localhost:${port}> or <nc localhost ${port}>.")
        for iTarget in range(1,getSetting('nTargets')+1):
            printAndLog(f"<target{iTarget}>: {getSetting('uartPipePort',targetId=iTarget)}")
        return

    def do_info(self,inp):
        """info
        Displays info about the running targets"""
        for iTarget in range(1,getSetting('nTargets')+1):
            printAndLog(f"<target{iTarget}>:")
            for xInfo in ['target', 'processor', 'osImage']:
                printAndLog(f"\t{xInfo} = {self.getTargetMember(iTarget,xInfo)}")
        return



    