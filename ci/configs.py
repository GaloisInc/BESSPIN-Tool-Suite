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
    ('binarySource',('GFE',)),
    ('openConsole',('No',)),
    ('useCustomOsImage',('No',)),
    ('useCustomBitfile',('No',))
}

unixDefaults = commonDefaults.union({
    ('buildApps',('no',)),
    ('appTimeout',(30,))
})

unixOnPremDefaults = unixDefaults.union({
    ('elfLoader',('netboot',)),
    ('netbootPortRangeStart',(5000,)),
    ('netbootPortRangeEnd',(6000,)),
    ('qemuNtkPortRangeStart',(5000,)),
    ('qemuNtkPortRangeEnd',(6000,))
})

unixAwsDefaults = unixDefaults.union({
    ('elfLoader',('JTAG',))
})

unixAllTargets_onprem = unixOnPremDefaults.union({
    ('processor',('chisel_p2', 'bluespec_p2',)),
    ('target',('qemu', 'fpga',)),
    ('osImage',('FreeBSD', 'debian',))
})

unixDevPR_onprem = unixOnPremDefaults.union({
    ('processor',('chisel_p2',)),
    ('target',('fpga',)),
    ('osImage',('FreeBSD', 'debian',))
})

unixDevPR_aws = unixAwsDefaults.union({
    ('processor',('chisel_p2',)),
    ('target',('aws',)),
    ('osImage',('debian',))
})

freertosDefaults = commonDefaults.union({
    ('osImage',('FreeRTOS',)),
    ('elfLoader',('JTAG',)),
    ('buildApps',('yes',)),
    ('appTimeout',(90,)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',))
})

freertosAllTargets_onprem = freertosDefaults.union({
    ('processor',('chisel_p1',)),
    ('target',('fpga',))
})

freertosDevPR_onprem = freertosAllTargets_onprem

freertosDevPR_aws = freertosDefaults.union({
    ('processor',('chisel_p1',)),
    ('target',('aws',))
})

appSets = {
    'runPeriodic' : {
        'freertos' : { 'freertos' : freertosAllTargets_onprem },
        'unix' : { 'unix' : unixAllTargets_onprem }
    },
    'runDevPR' : {
        'freertos' : { 'freertos' : freertosDevPR_onprem },
        'unix' : { 'unix' : unixDevPR_onprem },
        'aws' : { 'unix' : unixDevPR_aws, 'freertos' : freertosDevPR_aws }
    }
}
appSets['runRelease'] = appSets['runPeriodic']

