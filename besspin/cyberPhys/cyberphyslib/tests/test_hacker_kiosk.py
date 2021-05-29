import cyberphyslib.canlib as ccan

import cmd

class TestTcpBus(cmd.Cmd):
    intro = 'Welcome to cyberPhys interactive cmd shell. Type help or ? to list commands.\n'
    prompt = '(cyberPhys) '
    def __init__(self):
        super(TestTcpBus, self).__init__()
        print("Connecting Transmitter Thread...(Adjust the host and node IPs to your host")
        self.cmdPort = 5041
        self.host = f"10.88.88.3:{self.cmdPort}" # Hacker kiosk
        self.nodes = [f"10.88.88.1:{self.cmdPort}",
                      f"10.88.88.2:{self.cmdPort}",
                      f"10.88.88.3:{self.cmdPort}",
                      f"10.88.88.4:{self.cmdPort}"]
        self.canbus = ccan.TcpBus(self.host, self.nodes)

    def preloop(self):
        print(f"<{self.__class__.__name__}> preloop")
    
    def postloop(self):
        print(f"<{self.__class__.__name__}> postloop")
    
    def emptyline(self): #to avoid repeating the last command on <enter>
        return
    def do_quit(self,inp):
        print("Qutting")

if __name__ == '__main__':
    TestTcpBus().cmdloop()
