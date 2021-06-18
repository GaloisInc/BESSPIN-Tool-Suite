#!/bin/bash
PORT=5002

for TEST in --test ""
do
    for HACK_TYPE in throttle brake gear lkas
    do
        # Target1
        IP="10.88.88.12"
        SUFFIX="_baseline"
        # 1) ${HACK_TYPE}Nominal_baseline
        ./hack-ecu.py --port $PORT --type $HACK_TYPE --ip $IP --nominal ${TEST}
        mv j1939hack/hack.elf ${HACK_TYPE}Nominal${SUFFIX}${TEST}
        # 2) ${HACK_TYPE}Hacked_baseline
        ./hack-ecu.py --port $PORT --type $HACK_TYPE --ip $IP ${TEST}
        mv j1939hack/hack.elf ${HACK_TYPE}Hacked${SUFFIX}${TEST}

        # Target2
        IP="10.88.88.22"
        SUFFIX="_ssithInfo"
        # 1) ${HACK_TYPE}Nominal_baseline
        ./hack-ecu.py --port $PORT --type $HACK_TYPE --ip $IP --nominal ${TEST}
        mv j1939hack/hack.elf ${HACK_TYPE}Nominal${SUFFIX}${TEST}
        # 2) ${HACK_TYPE}Hacked_baseline
        ./hack-ecu.py --port $PORT --type $HACK_TYPE --ip $IP ${TEST}
        mv j1939hack/hack.elf ${HACK_TYPE}Hacked${SUFFIX}${TEST}

        # Target3
        IP="10.88.88.32"
        SUFFIX="_ssithEcu"
        # 1) ${HACK_TYPE}Nominal_baseline
        ./hack-ecu.py --port $PORT --type $HACK_TYPE --ip $IP --nominal ${TEST}
        mv j1939hack/hack.elf ${HACK_TYPE}Nominal${SUFFIX}${TEST}
        # 2) ${HACK_TYPE}Hacked_baseline
        ./hack-ecu.py --port $PORT --type $HACK_TYPE --ip $IP ${TEST}
        mv j1939hack/hack.elf ${HACK_TYPE}Hacked${SUFFIX}${TEST}
    done
done