#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This file provide the combinations of CI files generated.
--- Every combination is represented as a set of tuples. 
    Each tuple represents one setting and its possible values.
    Each "values" should be a tuple. Please note that a 1-element tuple should be: ('element',)
"""

fettTargetAMI = 'ami-0747018f37927b976' #fett-target-071120-89f0e8f / FETT AMI 89f0e8f61c5c392f8b1fa0759484c11066954d4b - image to test fix for FreeRTOS dying of loneliness

ciAWSqueue = 'https://sqs.us-west-2.amazonaws.com/845509001885/ssith-fett-target-ci-develop-pipeline-PipelineSQSQueue-1IOF3D3BU1MEP.fifo'
ciAWSbucket = 'ssith-fett-target-ci-develop'
ciAWSqueueNightly = 'https://sqs.us-west-2.amazonaws.com/363527286999/nightly-testing-queue.fifo'
ciAWSbucketNightly = 'nightly-testing-bucket'

commonDefaults = {
    ('mode',('test',)),
    ('openConsole',('No',)),
    ('useCustomOsImage',('No',)),
    ('useCustomProcessor',('No',)),
    ('productionTargetIp',('172.31.30.56',))
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
    ('elfLoader',('JTAG',)),
    ('target',('aws',))
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

gfe_debianDevPR_aws = gfe_unixAwsDefaults.union({
    ('processor',('chisel_p2',)),
    ('osImage',('debian',))
})

gfe_freebsdDevPR_aws = gfe_unixAwsDefaults.union({
    ('processor',('bluespec_p2',)),
    ('osImage',('FreeBSD',))
})

mit_unixDevPR_aws = unixDefaults.union({
    ('binarySource',('MIT',)),
    ('elfLoader',('JTAG',)),
    ('processor',('bluespec_p2',)),
    ('target',('aws',)),
    ('osImage',('debian',))
})

lmco_unixDevPR_aws = unixDefaults.union({
    ('binarySource',('LMCO',)),
    ('elfLoader',('JTAG',)),
    ('processor',('chisel_p2',)),
    ('target',('aws',)),
    ('osImage',('debian',))
})

sri_cambridge_unixDevPR_aws = unixDefaults.union({
    ('binarySource',('SRI-Cambridge',)),
    ('elfLoader',('JTAG',)),
    ('processor',('bluespec_p2',)),
    ('target',('aws',)),
    ('osImage',('FreeBSD',))
})

freertosDefaults = commonDefaults.union({
    ('osImage',('FreeRTOS',)),
    ('elfLoader',('JTAG',)),
    ('FreeRTOSUseRAMDisk',('no',))
})

gfe_freertosAllTargets_onprem = freertosDefaults.union({
    ('binarySource',('GFE',)),
    ('processor',('chisel_p1',)),
    ('target',('fpga',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',)),
    ('buildApps',('yes',))
})

gfe_freertosDevPR_onprem = gfe_freertosAllTargets_onprem

gfe_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('GFE',)),
    ('processor',('chisel_p1',)),
    ('target',('aws',)),
    ('cross-compiler',('GCC','Clang',)),
    ('linker',('GCC',)), # If cross-compiler is Clang, linker will be over-written to LLD
    ('buildApps',('no',))
})

lmco_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('LMCO',)),
    ('processor',('chisel_p1',)),
    ('target',('aws',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',)), # If cross-compiler is Clang, linker will be over-written to LLD
    ('buildApps',('no',))
})

michigan_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('Michigan',)),
    ('processor',('chisel_p1',)),
    ('target',('aws',)),
    ('buildApps',('no',))
})

appSets = {
    'runPeriodic' : {
        'freertos' : { 'gfe_freertos' : gfe_freertosAllTargets_onprem },
        'unix' : { 'gfe_unix' : gfe_unixAllTargets_onprem }
    },
    'runDevPR' : {
        'freertos' : { 'gfe_freertos' : gfe_freertosDevPR_onprem },
        'unix' : { 'gfe_unix' : gfe_unixDevPR_onprem },
        'aws' : { 'gfe_debian' : gfe_debianDevPR_aws, 
                'gfe_freebsd' : gfe_freebsdDevPR_aws, 
                'gfe_freertos' : gfe_freertosDevPR_aws,
                'lmco_freertos' : lmco_freertosDevPR_aws,
                'michigan_freertos' : michigan_freertosDevPR_aws,
                'mit_unix' : mit_unixDevPR_aws,
                'lmco_unix' : lmco_unixDevPR_aws,
                'sri-cambridge_unix' : sri_cambridge_unixDevPR_aws}
    }
}
appSets['runRelease'] = appSets['runPeriodic']

