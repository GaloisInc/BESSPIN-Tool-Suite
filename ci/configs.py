#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This file provide the combinations of CI files generated.
--- Every combination is represented as a set of tuples. 
    Each tuple represents one setting and its possible values.
    Each "values" should be a tuple. Please note that a 1-element tuple should be: ('element',)
"""

commonDefaults = {
    ('openConsole',('No',)),
    ('useCustomOsImage',('No',)),
    ('netbootPortRangeStart',(5000,)),
    ('netbootPortRangeEnd',(6000,)),
    ('qemuNtkPortRangeStart',(5000,)),
    ('qemuNtkPortRangeEnd',(6000,)),
    ('qemuSshHostPort',(2222,)),
    ('appTimeout',(30,))
}

unixDefaults = commonDefaults.union({
    ('processor',('chisel_p2', 'bluespec_p2',)),
    ('target',('qemu', 'fpga',)),
    ('osImage',('FreeBSD', 'debian',)),
    ('elfLoader',('netboot',)),
    ('buildApps',('no',))
})

webserver = unixDefaults.union({
    ('webserver',('yes',)),
    ('database',('no',)),
    ('voting',('no',))
})

database = unixDefaults.union({
    ('database',('yes',)),
    ('webserver',('no',)),
    ('voting',('no',))
})

freertos = commonDefaults.union({
    ('processor',('chisel_p1', 'bluespec_p1',)),
    ('target',('fpga',)),
    ('osImage',('FreeRTOS',)),
    ('elfLoader',('JTAG',)),
    ('database',('no',)),
    ('webserver',('no',)),
    ('voting',('no',)),
    ('buildApps',('yes',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',))
})

appSets = {'freertos':freertos, 'webserver':webserver, 'database':database}

