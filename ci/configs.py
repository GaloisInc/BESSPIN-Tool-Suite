#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This file provide the combinations of CI files generated.
--- Every combination is represented as a set of tuples. 
    Each tuple represents one setting and its possible values.
    Each "values" should be a tuple. Please note that a 1-element tuple should be: ('element',)
"""

commonDefaults = {
    ('mode',('test',)),
    ('openConsole',('No',)),
    ('useCustomOsImage',('No',)),
    ('useCustomBitfile',('No',)),
    ('binarySource',('GFE',)),
    ('appTimeout',(30,))
}

unixDefaults = commonDefaults.union({
    ('elfLoader',('netboot',)),
    ('buildApps',('no',)),
    ('netbootPortRangeStart',(5000,)),
    ('netbootPortRangeEnd',(6000,)),
    ('qemuNtkPortRangeStart',(5000,)),
    ('qemuNtkPortRangeEnd',(6000,))
})

unixAllTargets = unixDefaults.union({
    ('processor',('chisel_p2', 'bluespec_p2',)),
    ('target',('qemu', 'fpga',)),
    ('osImage',('FreeBSD', 'debian',))
})

unixDevPR = unixDefaults.union({
    ('processor',('chisel_p2',)),
    ('target',('fpga',)),
    ('osImage',('FreeBSD', 'debian',))
})

freertosDefaults = commonDefaults.union({
    ('osImage',('FreeRTOS',)),
    ('elfLoader',('JTAG',)),
    ('buildApps',('yes',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',))
})

freertosAllTargets = freertosDefaults.union({
    ('processor',('chisel_p1',)),
    ('target',('fpga',))
})

freertosDevPR = freertosDefaults.union({
    ('processor',('chisel_p1',)),
    ('target',('fpga',))
})

appSets = {
    'runPeriodic' : {
        'freertos' : {'freertos':freertosAllTargets},
        'unix' : {'unix':unixAllTargets}
    },
    'runDevPR' : {
        'freertos' : {'freertos':freertosDevPR},
        'unix' : {'unix':unixDevPR}
    }
}
appSets['runRelease'] = appSets['runPeriodic']

