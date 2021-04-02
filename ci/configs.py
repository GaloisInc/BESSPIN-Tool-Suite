#! /usr/bin/env python3
"""
--- besspin-ci.py is the CI entry to the BESSPIN program. 
--- This file provide the combinations of CI files generated.
--- Every combination is represented as a set of tuples. 
    Each tuple represents one setting and its possible values.
    Each "values" should be a tuple. Please note that a 1-element tuple should be: ('element',)
"""
backupBesspinAMI = { 'ImageId' : 'ami-07fc3f8f4525f1c94', 
                'CreationDate' : '2020-09-08T16:28:43.000Z',
                'OwnerId' : '363527286999'} 
# Please update occasionally. Used by ./utils.getBesspinAMI() instead of erring.

ciAWSqueue = 'https://sqs.us-west-2.amazonaws.com/845509001885/ssith-fett-target-ci-develop-pipeline-PipelineSQSQueue-1IOF3D3BU1MEP.fifo'
ciAWSbucket = 'ssith-fett-target-ci-develop'
ciAWSqueueTesting = 'https://sqs.us-west-2.amazonaws.com/363527286999/aws-test-suite-queue.fifo'
ciAWSbucketTesting = 'aws-test-suite-bucket'

commonDefaults = {
    ('openConsole',('No',)),
    ('gdbDebug',('No',)),
    ('useCustomHwTarget',('No',)),
    ('useCustomTargetIp',('No',)),
    ('useCustomQemu',('No',)),
    ('useCustomOsImage',('No',)),
    ('useCustomProcessor',('No',)),
    ('productionTargetIp',('172.31.30.56',))
}

commonDefaultsFETT = {
    ('mode',('fettTest',))
}

commonDefaultsCWEs = {
    ('mode',('evaluateSecurityTests',)),
    ('vulClasses', ('[bufferErrors, PPAC, resourceManagement, informationLeakage, numericErrors, hardwareSoC, injection]',)),
    ('useCustomScoring',('No',)),
    ('useCustomCompiling',('No',)),
    ('FreeRTOStimeout',(10,)),
    ('runAllTests',('Yes',)),
    ('runUnixMultitaskingTests',('Yes',)),
    ('instancesPerTestPart',(1,))
}

unixDefaultsCWEs = commonDefaultsCWEs.union({
    ('nTests',(100,)),
    ('cross-compiler',('GCC','Clang',)), # If cross-compiler is Clang, linker will be over-written to LLD
    ('linker',('GCC',)),
})

freertosDefaultsCWEs = commonDefaultsCWEs.union({
    ('nTests',(40,))
})

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
    ('sourceVariant',('default',))
})

gfe_unixAwsDefaults = unixDefaults.union({
    ('binarySource',('GFE',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default',)),
    ('target',('awsf1',))
})

gfe_unixAllTargets_onprem = gfe_unixOnPremDefaults.union({
    ('processor',('chisel_p2', 'bluespec_p2',)),
    ('target',('qemu', 'vcu118',)),
    ('osImage',('FreeBSD', 'debian',))
})

gfe_unixDevPR_onprem = gfe_unixOnPremDefaults.union({
    ('processor',('chisel_p2',)),
    ('target',('vcu118',)),
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
    ('target',('awsf1',)),
    ('osImage',('debian',))
})

lmco_unixDevPR_aws = unixDefaults.union({
    ('binarySource',('LMCO',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default',)),
    ('processor',('chisel_p2',)),
    ('target',('awsf1',)),
    ('osImage',('debian',))
})

sri_cambridge_unixDevPR_aws = unixDefaults.union({
    ('binarySource',('SRI-Cambridge',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default','purecap','temporal',)),
    ('processor',('bluespec_p2',)),
    ('target',('awsf1',)),
    ('osImage',('FreeBSD',))
})

freertosDefaults = commonDefaults.union({
    ('osImage',('FreeRTOS',)),
    ('elfLoader',('JTAG',)),
    ('sourceVariant',('default',)),
    ('freertosFatFs',('default',))
})

gfe_freertosAllTargets_onprem = freertosDefaults.union({
    ('binarySource',('GFE',)),
    ('processor',('chisel_p1',)),
    ('target',('vcu118',)),
    ('cross-compiler',('GCC','Clang',)),
    ('linker',('GCC',)),
    ('buildApps',('yes',))
})

gfe_freertosDevPR_onprem = gfe_freertosAllTargets_onprem

gfe_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('GFE',)),
    ('processor',('chisel_p1',)),
    ('target',('awsf1',)),
    ('cross-compiler',('GCC','Clang',)),
    ('linker',('GCC',)), # If cross-compiler is Clang, linker will be over-written to LLD
    ('buildApps',('yes',))
})

lmco_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('LMCO',)),
    ('processor',('chisel_p1',)),
    ('target',('awsf1',)),
    ('cross-compiler',('GCC',)),
    ('linker',('GCC',)), # If cross-compiler is Clang, linker will be over-written to LLD
    ('buildApps',('yes',))
})

michigan_freertosDevPR_aws = freertosDefaults.union({
    ('binarySource',('Michigan',)),
    ('processor',('chisel_p1',)),
    ('target',('awsf1',)),
    ('buildApps',('no',))
})

appSets = {
    'runPeriodic' : {
        'OnPrem' : {
            'fett' : {
                'gfe_freertos' : gfe_freertosAllTargets_onprem.union(commonDefaultsFETT),
                'gfe_unix' : gfe_unixAllTargets_onprem.union(commonDefaultsFETT)
            },
            'cwe' : {
                'gfe_freertos' : gfe_freertosAllTargets_onprem.union(freertosDefaultsCWEs),
                'gfe_unix' : gfe_unixAllTargets_onprem.union(unixDefaultsCWEs)
            }
        }
    },
    'runDevPR' : {
        'OnPrem' : {
            'fett' : {
                'gfe_freertos' : gfe_freertosDevPR_onprem.union(commonDefaultsFETT),
                'gfe_unix' : gfe_unixDevPR_onprem.union(commonDefaultsFETT)
            },
            'cwe' : {
                'gfe_freertos' : gfe_freertosDevPR_onprem.union(freertosDefaultsCWEs),
                'gfe_unix' : gfe_unixDevPR_onprem.union(unixDefaultsCWEs)
            }
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
                'gfe_debian' : gfe_debianDevPR_aws.union(unixDefaultsCWEs), 
                'gfe_freebsd' : gfe_freebsdDevPR_aws.union(unixDefaultsCWEs), 
                'gfe_freertos' : gfe_freertosDevPR_aws.union(freertosDefaultsCWEs)
            }
        }
    }
}
appSets['runRelease'] = appSets['runPeriodic']

