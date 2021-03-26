# test
# Run with:
# 1) export PYTHONPATH=`pwd`/../python
# 2) python3 ./zmqtest.py
#
from can import Message
from canlib import CommandBus

def main():
    IP_ADMIN_PC = "127.0.0.1:5555"
    IP_SIM_PC = "127.0.0.1:5556"
    IP_HACKER_KIOSK = "127.0.0.1:5557"
    IP_INFOTAINMENT_THIN_CLIENT = "127.0.0.1:5558"


    nodes = [IP_ADMIN_PC, IP_SIM_PC, IP_HACKER_KIOSK, IP_INFOTAINMENT_THIN_CLIENT]
    admin_pc = CommandBus(IP_ADMIN_PC, nodes)
    kiosk = CommandBus(IP_HACKER_KIOSK, nodes)
    sim_pc = CommandBus(IP_SIM_PC, nodes)
    
    
    tx = Message(arbitration_id=0XAAFEEB04, dlc=1,data=b'x')
    admin_pc.send(tx)
    msg = sim_pc.recv(timeout=0.1)
    print(f"SIMPC RX: {msg}")
    msg = kiosk.recv(timeout=0.1)
    print(f"KIOSK RX: {msg}")
    admin_pc.send(tx)
    msg = sim_pc.recv(timeout=0.1)
    print(f"SIMPC RX: {msg}")
    msg = kiosk.recv(timeout=0.1)
    print(f"KIOSK RX: {msg}")
    admin_pc.send(tx)
    msg = kiosk.recv(timeout=0.1)
    print(f"KIOSK RX: {msg}")
    msg = sim_pc.recv(timeout=0.1)
    print(f"SIMPC RX: {msg}")
    print("Done!")


if __name__ == "__main__":
    main()
