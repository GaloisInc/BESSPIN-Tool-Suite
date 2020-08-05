#! /usr/bin/env bash
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Runs testgen for PPAC
# Usage: Please DO NOT USE DIRECTLY. [All sanity checks are done in ../testgen.sh]
# Follow instructions in ../testgen.sh instead
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Setting up the environment-----------------------------------------------------
fileName=`basename $0`
vulClass=PPAC
id=2
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)" #BASE_DIR should be the ${id}_${vulClass^} directory
setupEnv=$1
source $setupEnv $BASE_DIR $id $vulClass 
if [ $? -ne 0 ]; then "Error in $fileName: Failed to load configurations for <$vulClass>."; exit 1; fi 
echo "$fileName: Configuration loaded succesffully." |& tee -a $reportFile

# Prepare the tests--------------------------------------------------------------
if [ $pocExploitsMode -ne 1 ]; then #normal mode-- testgen
    mkdir $testsDir
    genParameters=$gSCRIPTS/genTestParameters.py
    checkFile $genParameters "Error in $fileName: The parameters generation script <$genParameters> not found."
    $genParameters $randomizeParameters $configFile $configDataJsonFile $testsDir $vulClass $reportFile 2>> $reportFile
    isError $? "Error in $fileName: Failed to generate the test parameters." 
    checkFile $testsDir/testsParameters.h "Error in $fileName: The tests configuration parameters <$testsDir/testsParameters.h> not found."
    echo "#define SPOOFING_IP \"$spoofingIP\"" >> $testsDir/testsParameters.h 2>> $reportFile
    echo "#define TCP_PORT_NUMBER $FPGANTK_PORT_TARGET" >> $testsDir/testsParameters.h 2>> $reportFile
    if [[ $osImage == "FreeRTOS" ]]; then
        cp $vBASE_DIR/sources/test_*.c $testsDir/
        cp -r $vBASE_DIR/sources/libFreeRTOS $testsDir/lib
        if [[ $XLEN == 64 ]]; then
            cp $vSCRIPTS/extraMemForFreeRTOS.ld $testsDir/
        fi
        $vSCRIPTS/genCertificates.sh $setupEnv $BASE_DIR $id $vulClass $testsDir 2>> $reportFile
        isError $? "Error in $fileName: Failed to generate certificates used by TLS."
        timeOfDay=$(date +%s)
        safeTimeOfDay=$(expr $((timeOfDay)) + 300) #add 5 minutes to be safe
        echo -e "\n#define FAKETIMEOFDAY $safeTimeOfDay\n" >> $testsDir/testsParameters.h
        #seeds for WolfSSL
        if [ $useSeedForWolfSSL -eq 1 ]; then #use the user configured seed
            echo -e "#define TESTGEN_WC_SEEDS $seedForWolfSSL\n" >> $testsDir/testsParameters.h
            echo -e "#define TESTGEN_WC_SEEDS_LEN 1\n" >> $testsDir/testsParameters.h
        else #generate seeds
            RANDOM=$$ #inialize the seed to pid
            genSeeds=()
            for iSeed in [$(seq ${nSeedsForWolfSSL})] ; do
                xSeed=$(($RANDOM%256))
                genSeeds+=("$xSeed")
            done
            echo -e "#define TESTGEN_WC_SEEDS $(echo ${genSeeds[*]} | sed "s/ /,/g")\n" >> $testsDir/testsParameters.h
            echo -e "#define TESTGEN_WC_SEEDS_LEN $nSeedsForWolfSSL\n" >> $testsDir/testsParameters.h
        fi
    else
        for xConfFile in $(ls $vBASE_DIR/sources/*_${osImage}); do #pam and .conf files
            xConfFileName=$(basename $xConfFile)
            cp $xConfFile $testsDir/${xConfFileName/_${osImage}/}
        done
        cp $vBASE_DIR/sources/test_*.c $testsDir/
    fi
    echo "$fileName: Tests prepared successfully." |& tee -a $reportFile
else #poc-exploits
    if [[ $osImage == "FreeRTOS" ]]; then
        isError 1 "Error in $fileName: PPAC POCs are not yet implemented to run on $osImage."
    fi
    echo "$fileName: testgen is running in <poc-exploits> mode." |& tee -a $reportFile
    mkdir $testsDir
    checkFile $collectPOCs "Error in $fileName: The POCs collection script <$collectPOCs> not found."
    $collectPOCs $setupEnv $BASE_DIR $id $vulClass $testsDir
    retCollect=$?
    if [ $retCollect -eq 100 ]; then
        :  #do nothing
    elif [ $retCollect -ne 0 ]; then
        echo "Error in $fileName: Unable to collect the POCs."
        exit 1
    fi
fi

# 2. Execute the test on the chosen backend----------------------------------------
# ------ backend
if [[ $backend == "qemu" ]] || [[ $backend == "fpga" ]]; then
    checkFile $emuDirExec "Error in $fileName: Execution file for <$backend emulation> of a directory <$emuDirExec> not found."
    $emuDirExec $setupEnv $BASE_DIR $id $vulClass $testsDir
    isError $? "Error in $fileName: Failed to run $backend emulation." 
    echo "$fileName: $backend emulation ran successfully." |& tee -a $reportFile

elif [[ $backend == "simulation" ]]; then
    echo "Warning in $fileName: Simulation for <$vulClass> is implemented for bare metal only"
    if [ $debugMode -eq 1 ]; then echo "Warning in $fileName: <debugMode> is not yet implemented for <$vulClass.simulation>. This option will be ignored."; fi
    checkFile $simDirBareExec "Error in $fileName: Execution file for bare metal simulation of a directory <$simDirBareExec> not found."
    $simDirBareExec $setupEnv $BASE_DIR $id $vulClass $testsDir
    isError $? "Error in $fileName: Failed to run simulation." 
    echo "$fileName: Simulation ran successfully." |& tee -a $reportFile
    
else
    echo "Error in $fileName: This should never happen. Did you execute <testgen_${vulClass^}> directly? Please use ../testgen.sh instead!" |& tee -a $reportFile
    exit 1
fi 

if [ $multiVulClasses -eq 1 ]; then
    waitForFile $doTheScoringFile 3
fi

if [ $pocExploitsMode -ne 1 ] && [[ $partialRun != "onlyBuild" ]]; then
    #count the results
    echo -e "\n$fileName: Scoring the test results..."
    $gSCRIPTS/scoreTests.py $vSCRIPTS/cweScores/__init__.py $testsDir $reportFile $useCustomScoring $customizedScoringConfigFile
    isError $? "Error in $fileName: Failed to score the test results." "$fileName: Tests results scored successfully!" 
fi

if [ $multiVulClasses -eq 1 ]; then
    echo 'SUCCESS' > $execResultFile
fi 
