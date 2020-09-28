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

    def precmd(self, line):
        if (line != 'EOF'):
            line = line.lower()
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
            xTarget = getSetting('targetObj',targetId=iTarget)
            if (hasattr(xTarget,'ipTarget')):
                xIp = xTarget.ipTarget
            else:
                xIp = 'UNKNOWN' 
            printAndLog(f"<target{iTarget}>: {xIp}")
        return

    