#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This file provide the combinations of CI files generated.
--- Every combination is represented as a set of tuples. 
    Each tuple represents one setting and its possible values.
    Each "values" should be a tuple. Please note that a 1-element tuple should be: ('element',)
"""
backupFettAMI = { 'ImageId' : 'ami-07fc3f8f4525f1c94', 
                'CreationDate' : '2020-09-08T16:28:43.000Z',
                'OwnerId' : '363527286999'} 
# Please update occasionally. Used by ./utils.getFettTargetAMI() instead of erring.

ciAWSqueue = 'https://sqs.us-west-2.amazonaws.com/845509001885/ssith-fett-target-ci-develop-pipeline-PipelineSQSQueue-1IOF3D3BU1MEP.fifo'
ciAWSbucket = 'ssith-fett-target-ci-develop'
ciAWSqueueTesting = 'https://sqs.us-west-2.amazonaws.com/363527286999/aws-test-suite-queue.fifo'
ciAWSbucketTesting = 'aws-test-suite-bucket'

commonDefaults = {
    ('openConsole',('No',)),
    ('useCustomOsImage',('No',)),
    ('useCustomProcessor',('No',)),
    ('productionTargetIp',('172.31.30.56',))
}

commonDefaultsFETT = {
    ('mode',('test',))
}

commonDefaultsCWEs = {
    ('mode',('evaluateSecurityTests',)),
    ('vulClasses', ('[bufferErrors, PPAC, resourceManagement, informationLeakage, numericErrors]',)),
    ('useCustomScoring',('No',)),
    ('useCustomCompiling',('No',)),
    ('FreeRTOStimeout',(10,)),
    ('runAllTests',('Yes',)),
    ('randomizeParameters',('No',)),
    ('nTests',(100,))
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
    ('sourceVariant',('default',)),
    ('netbootPortRangeStart',(5000,)),
    ('netbootPortRangeEnd',(6000,)),
    ('qemuNtkPortRangeStart',(5000,)),
    ('qemuNtkPortRangeEnd',(6000,))
})

gfe_unixAwsDefaults = unixDefaults.union({
    ('binarySource',('GFE',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default',)),
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
    ('sourceVariant',('default',)),
    ('processor',('bluespec_p2',)),
    ('target',('aws',)),
    ('osImage',('debian',))
})

lmco_unixDevPR_aws = unixDefaults.union({
    ('binarySource',('LMCO',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default',)),
    ('processor',('chisel_p2',)),
    ('target',('aws',)),
    ('osImage',('debian',))
})

sri_cambridge_unixDevPR_aws = unixDefaults.union({
    ('binarySource',('SRI-Cambridge',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default','purecap','temporal',)),
    ('processor',('bluespec_p2',)),
    ('target',('aws',)),
    ('osImage',('FreeBSD',))
})

freertosDefaults = commonDefaults.union({
    ('osImage',('FreeRTOS',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default',)),
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
    ('buildApps',('yes',))
})

lmco_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('LMCO',)),
    ('processor',('chisel_p1',)),
    ('target',('aws',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',)), # If cross-compiler is Clang, linker will be over-written to LLD
    ('buildApps',('yes',))
})

michigan_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('Michigan',)),
    ('processor',('chisel_p1',)),
    ('target',('aws',)),
    ('buildApps',('no',))
})

appSets = {
    'runPeriodic' : {
        'freertos' : {
            'fett' : { 'gfe_freertos' : gfe_freertosAllTargets_onprem.union(commonDefaultsFETT) },
            'cwe' : { 'gfe_freertos' : gfe_freertosAllTargets_onprem.union(commonDefaultsCWEs) }
        },
        'unix' : {
            'fett' : { 'gfe_unix' : gfe_unixAllTargets_onprem.union(commonDefaultsFETT) },
            'cwe' : { 'gfe_unix' : gfe_unixAllTargets_onprem.union(commonDefaultsCWEs) }
        }
    },
    'runDevPR' : {
        'freertos' : {
            'fett' : { 'gfe_freertos' : gfe_freertosDevPR_onprem.union(commonDefaultsFETT) },
            'cwe' : { 'gfe_freertos' : gfe_freertosDevPR_onprem.union(commonDefaultsCWEs) }
        },
        'unix' : {
            'fett' : { 'gfe_unix' : gfe_unixDevPR_onprem.union(commonDefaultsFETT) },
            'cwe' : { 'gfe_unix' : gfe_unixDevPR_onprem.union(commonDefaultsCWEs) }
        },
        'aws' : {
            'fett' : { 
                'gfe_debian' : gfe_debianDevPR_aws.union(commonDefaultsFETT), 
                'gfe_freebsd' : gfe_freebsdDevPR_aws.union(commonDefaultsFETT), 
                'gfe_freertos' : gfe_freertosDevPR_aws.union(commonDefaultsFETT),
                'lmco_freertos' : lmco_freertosDevPR_aws.union(commonDefaultsFETT),
                'michigan_freertos' : michigan_freertosDevPR_aws.union(commonDefaultsFETT),
                'mit_unix' : mit_unixDevPR_aws.union(commonDefaultsFETT),
                'lmco_unix' : lmco_unixDevPR_aws.union(commonDefaultsFETT),
                'sri-cambridge_unix' : sri_cambridge_unixDevPR_aws.union(commonDefaultsFETT)
            },
            'cwe' : { 
                'gfe_debian' : gfe_debianDevPR_aws.union(commonDefaultsCWEs), 
                'gfe_freebsd' : gfe_freebsdDevPR_aws.union(commonDefaultsCWEs), 
                'gfe_freertos' : gfe_freertosDevPR_aws.union(commonDefaultsCWEs)
            }
        }
    }
}
appSets['runRelease'] = appSets['runPeriodic']

