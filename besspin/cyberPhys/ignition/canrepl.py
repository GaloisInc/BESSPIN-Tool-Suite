"""
Project: SSITH CyberPhysical Demonstrator
Name: canrepl.py
Author: Ethan Lew <elew@galois.com>
Date: 16 April 2021

usage: canrepl.py [-h] [-port PORT] [-ip IP]

Can ID Canlib REPL

optional arguments:
  -h, --help  show this help message and exit
  -port PORT  IP of TCP Bus
  -ip IP      Port of TCP Bus
"""
import cyberphyslib.canlib as ccan
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import re
import struct
import argparse
import threading

session_str = \
"""CanLib CAN REPL

Send a CAN message:
    can console> <CANLIB IDENTIFIER> <STRUCT PACK STRING> <DATA>
Exit:
    can console> exit

Examples:
    can console> CMD_RESTART !B 0x01
    Formed Message: Timestamp:        0.000000    ID: aafeeb04    X                DLC:  1    01
"""

# argument parser
parser = argparse.ArgumentParser(description="Can ID Canlib REPL")
parser.add_argument("-port", type=int, default=5030, help="IP of TCP Bus")
parser.add_argument("-ip", type=str, default="127.0.0.1", help="Port of TCP Bus")
args = parser.parse_args()

# Setup the CAN Network
print("Connecting Transmitter Thread...")
IP_ADMIN_PC = f"{args.ip}:{args.port}"
nodes = ["127.0.0.1:5557", IP_ADMIN_PC]
admin_pc = ccan.TcpBus(IP_ADMIN_PC, nodes)

# Setup the prompt
canids = {name.split('CAN_ID_')[1]: getattr(ccan, name) for name in dir(ccan) if 'CAN_ID' in name}
can_completer = NestedCompleter.from_nested_dict({**{name: None for name in canids.keys() }, **{'exit': None}})
session = PromptSession('can console> ', completer=can_completer, auto_suggest=AutoSuggestFromHistory())

# for printing incoming messages
# this was too obnoxious for a single console application
#def recv_thread(evt: threading.Event):
#    recvr = ccan.TcpBus("127.0.0.1:5558", nodes)
#    canidsr = {v: k for k, v in canids.items()}
#    while not evt.is_set():
#        msg = recvr.recv(0.5)
#        if msg:
#            print(f"\nRECEIVED {canidsr[msg.arbitration_id]}:\n\t{msg}\n")
#print("Connecting Receiver Thread...")
#rfinish = threading.Event()
#rthread = threading.Thread(target=recv_thread, args=(rfinish,), daemon=True)
#rthread.start()

# Mainloop
not_finished = True
print(session_str)
while not_finished:
    text = session.prompt()
    if text == 'exit':
        not_finished = False
    else:
        try:
            res = re.split(r'([A-Z_]+) ([A-Za-z!]+) ',  text)[1:]
            assert len(res) == 3, f"<{text}> didn't match format of <can_id struct_format data>"
            cid = res[0]
            pack= res[1]
            data = res[2]
            data = eval(data)
            data = (data,) if not isinstance(data, tuple) else data
            msg = ccan.Message(arbitration_id=canids[cid], data=struct.pack(pack, *data))
            print(f"Formed Message: {msg}")
            admin_pc.send(msg)
        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"Encountered Error: {exc}")

#rfinish.set()
#rthread.join()