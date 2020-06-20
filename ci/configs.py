#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This file provide the combinations of CI files generated.
--- Every combination is represented as a set of tuples. 
    Each tuple represents one setting and its possible values.
    Each "values" should be a tuple. Please note that a 1-element tuple should be: ('element',)
"""

fettTargetAMI = 'ami-04c55ee64b3c6f758' #fett-target-060120
ciAWSqueue = 'https://sqs.us-west-2.amazonaws.com/845509001885/ssith-fett-target-ci-develop-pipeline-PipelineSQSQueue-1IOF3D3BU1MEP.fifo'
ciAWSbucket = 'ssith-fett-target-ci-develop'

commonDefaults = {
    ('mode',('test',)),
    ('openConsole',('No',)),
    ('useCustomOsImage',('No',)),
    ('useCustomProcessor',('No',)),
    ('awsJumpBoxIp',('172.31.30.56',))
}

unixDefaults = commonDefaults.union({
    ('useCustomCredentials',('yes',)),
    ('userName',('researcher',)),
    ('userPasswordHash',('$6$xcnc07LxM26Xq$VBAn8.ZfCzEf5MEpftSsCndDaxfPs5gXWjdrvrHcSA6O6eRoV5etd9V8E.BE0/q4P8pGOz96Nav3PPuXOktmv.',)),
    ('buildApps',('no',)),
    ('rootUserAccess',('yes',))
})

gfe_unixOnPremDefaults = unixDefaults.union({
    ('binarySource',('GFE',)),
    ('elfLoader',('netboot',)),
    ('netbootPortRangeStart',(5000,)),
    ('netbootPortRangeEnd',(6000,)),
    ('qemuNtkPortRangeStart',(5000,)),
    ('qemuNtkPortRangeEnd',(6000,))
})

gfe_unixAwsDefaults = unixDefaults.union({
    ('binarySource',('GFE',)),
    ('elfLoader',('JTAG',))
})

gfe_unixAllTargets_onprem = gfe_unixOnPremDefaults.union({
    ('processor',('chisel_p2', 'bluespec_p2',)),
    ('target',('qemu', 'fpga',)),
    ('osImage',('FreeBSD', 'debian',))
})

gfe_unixDevPR_onprem = gfe_unixOnPremDefaults.union({
    ('processor',('chisel_p2',)),
    ('target',('fpga',)),
    ('osImage',('FreeBSD', 'debian',))
})

gfe_unixDevPR_aws = gfe_unixAwsDefaults.union({
    ('processor',('chisel_p2',)),
    ('target',('aws',)),
    ('osImage',('debian',))
})

freertosDefaults = commonDefaults.union({
    ('osImage',('FreeRTOS',)),
    ('elfLoader',('JTAG',)),
    ('buildApps',('yes',))
})

gfe_freertosAllTargets_onprem = freertosDefaults.union({
    ('binarySource',('GFE',)),
    ('processor',('chisel_p1',)),
    ('target',('fpga',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',)) 
})

gfe_freertosDevPR_onprem = gfe_freertosAllTargets_onprem

gfe_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('GFE',)),
    ('processor',('chisel_p1',)),
    ('target',('aws',)),
    ('cross-compiler',('GCC','Clang',)),
    ('linker',('GCC',)) # If cross-compiler is Clang, linker will be over-written to LLD
})

lmco_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('LMCO',)),
    ('processor',('chisel_p1',)),
    ('target',('aws',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',)) # If cross-compiler is Clang, linker will be over-written to LLD
})

appSets = {
    'runPeriodic' : {
        'freertos' : { 'gfe_freertos' : gfe_freertosAllTargets_onprem },
        'unix' : { 'gfe_unix' : gfe_unixAllTargets_onprem }
    },
    'runDevPR' : {
        'freertos' : { 'gfe_freertos' : gfe_freertosDevPR_onprem },
        'unix' : { 'gfe_unix' : gfe_unixDevPR_onprem },
        'aws' : { 'gfe_unix' : gfe_unixDevPR_aws, 
                'gfe_freertos' : gfe_freertosDevPR_aws,
                'lmco_freertos' : lmco_freertosDevPR_aws}
    }
}
appSets['runRelease'] = appSets['runPeriodic']

