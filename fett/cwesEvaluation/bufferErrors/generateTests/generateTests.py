#!/usr/bin/env python3
import os
import sys

from fett.base.utils.misc import *
import fett.cwesEvaluation.utils.featureModelUtil as featureModelUtil
from fett.cwesEvaluation.bufferErrors.generateTests.bof_template import *
from fett.cwesEvaluation.bufferErrors.generateTests.bof_instance import *
from fett.cwesEvaluation.bufferErrors.generateTests.instanceSelector import *

def parseBytes(sz):
    try:
        if sz[-1] == 'K':
            return (1024*int(sz[:-1]))
        if sz[-1] == 'M':
            return (1024*1024*int(sz[:-1]))
        if sz[-1] == 'G':
            return (1024*1024*1024*int(sz[:-1]))
        return int(sz)
    except Exception as exc:
        logAndExit(f'<generateTests> Unable to parse size {sz}',
                   exc=exc,
                   exitCode=EXIT.Configuration)

def generateTests(outdir):
    # Check that nTests is large enough to avoid score instability
    minNTests = 40 if isEqSetting('osImage', 'FreeRTOS') else 100
    if getSettingDict('bufferErrors', 'nTests') < minNTests:
        warnAndLog(f"<generateTests> <nTests> must be at least <{minNTests}> "
                   f"for <{getSetting('osImage')}>.  Changing <nTests> to "
                   f"<{minNTests}>.")
        setSettingDict('bufferErrors', 'nTests', minNTests)

    bufferErrorsDir = os.path.join(getSetting("repoDir"),
                                   "fett",
                                   "cwesEvaluation",
                                   "bufferErrors")
    modelPath = (getSettingDict('bufferErrors', 'pathToCustomErrorModel') if
                 getSettingDict('bufferErrors', 'useCustomErrorModel') else
                 os.path.join(bufferErrorsDir, "BufferErrors.cfr"))
    try:
        model = featureModelUtil.loadFM(modelPath)
    except Exception as exc:
        logAndExit(f'<generateTests> Failed to load feature model {modelPath}',
                   exc=exc)
    printAndLog(f"<generateTests> Loaded model from {modelPath}")

    # Prune out other vulnerability classes
    model = featureModelUtil.splitFM(model, ["BufferErrors_Test"])[0]
    instancePath = os.path.join(bufferErrorsDir, "CachedInstances.json")
    if (getSettingDict('bufferErrors', 'useCachedInstances') and
        not getSettingDict('bufferErrors', 'useCustomErrorModel')):
        printAndLog("<generateTests> Loading cached instances "
                    f"<{instancePath}>")
        enumeratedFM = safeLoadJsonFile(instancePath)
    else:
        printAndLog(f"<generateTests> Sliced model {modelPath} with BufferErrors_Test")
        printAndLog("<generateTests> Enumerating instances...(this can take a while)")
        # Make sure that the buffer error test is actually enabled
        model = featureModelUtil.addConstraints(model, ["BufferErrors_Test"])
        enumeratedFM = featureModelUtil.enumerateFM(model)
        if not getSettingDict('bufferErrors', 'useCustomErrorModel'):
            printAndLog(f"<generateTests> Caching instances to <{instancePath}>")
            safeDumpJsonFile(enumeratedFM, instancePath)
        printAndLog("<generateTests> Done generating instances")
    instances = [BofInstance(model, x) for x in enumeratedFM]
    heapSize = parseBytes(getSettingDict('bufferErrors', 'heapSize'))
    stackSize = parseBytes(getSettingDict('bufferErrors', 'stackSize'))
    seed = (getSettingDict('bufferErrors', 'seed') if
            getSettingDict('bufferErrors', 'useSeed') else
            random.randrange(sys.maxsize))
    printAndLog(f"<generateTests> Using seed {seed}")

    tgs = [ (i, BofTestGen(i, heapSize, stackSize)) for i in instances ]
    rnd = random.Random(seed)

    printAndLog("<generateTests> Generating "
                f"{getSettingDict('bufferErrors', 'nTests')} tests "
                f"with seed={seed}, heap-size={heapSize}, "
                f"stack-size={stackSize}")
    if getSettingDict('bufferErrors', "nSkip"):
        printAndLog("<generateTests> Skipping {getSettingDict('bufferErrors', 'nSkip')} instances")
        for i in range(getSettingDict('bufferErrors', "nSkip")):
            tg = rnd.choice(tgs)
            tg.genInstance(rnd, drop=True)

    selector = InstanceSelector(tgs, rnd)
    for i in range(getSettingDict('bufferErrors', 'nTests')):
        # Name tests test_buffer_error_<i>.c to avoid conflicting with the
        # test_<i>.c tests in the other vulnerability classes
        out   = os.path.join(outdir, f"test_buffer_errors_{i}.c")
        outfd = ftOpenFile(out, "w")
        sys.stdout.write("\033[K")
        outfd.write(selector.chooseInstance().genInstance(rnd, drop=False))
        outfd.close()
    printAndLog("<generateTests> Done generating tests")

