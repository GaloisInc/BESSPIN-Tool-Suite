"""
Project: SSITH CyberPhysical Demonstrator
Name: joystick_test.py
Author: Ethan Lew <elew@galois.com>
Date: 02 June 2021

View Joystick Input Traces

Rename the variable joy_name to configure
"""
from cyberphyslib.demonstrator.joystick import *

# Rename this
joy_name = 'FANATEC Podium Wheel Base DD1'


def get_all_joysticks():
    """return list of all joysticks"""
    pygame.init()
    return [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]


def list_joysticks():
    """return list of all joystick names"""
    joysticks = get_all_joysticks()
    return [joy.get_name() for joy in joysticks]


def joy_info(joy: pygame.joystick.Joystick) -> str:
    """information string of a joystick object"""
    ostr = joy.get_name()
    ostr += '\t\n' +  f"Number of trackballs: {joy.get_numballs()}"
    ostr += '\t\n' + f"Number of buttons: {joy.get_numbuttons()}"
    ostr += '\t\n' + f"Number of axes: {joy.get_numaxes()}"
    ostr += '\t\n' + f"Number of hats: {joy.get_numhats()}"
    return ostr


# print joystick parameters and traces
#pygame.init()
#joystick = init_joystick(joy_name)
#joystick.init()
#print(list_joysticks())
#print(joy_info(joystick))
#while True:
#    _ = pygame.event.get()  # TODO: is this necessary?
#    ret = [joystick.get_axis(idx) for idx in range(joystick.get_numaxes())]
#    print(ret)
#    ret = [joystick.get_hat(idx) for idx in range(joystick.get_numhats())]
#    print(ret)
jmc =JoystickMonitorComponent(joy_name, window_length=20)
jmc.start()
while True:
    pass