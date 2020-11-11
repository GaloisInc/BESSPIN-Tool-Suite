#!/usr/bin/env python3
import os
import sys

from fett.base.utils.misc import *
import fett.cwesEvaluation.utils.featureModelUtil as featureModelUtil
from fett.cwesEvaluation.bufferErrors.generateTests.bof_template import *
from fett.cwesEvaluation.bufferErrors.generateTests.bof_instance import *

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
    # TODO: Configurable model
    modelPath = os.path.join(getSetting("repoDir"),
                             "fett",
                             "cwesEvaluation",
                             "bufferErrors",
                             "BufferErrors.cfr")
    try:
        model = featureModelUtil.loadFM(modelPath)
    except Exception as exc:
        logAndExit(f'<generateTests> Failed to load feature model {modelPath}',
                   exc=exc)
    printAndLog(f"<generateTests> Loaded model from {modelPath}")

    # Prune out other vulnerability classes
    model = featureModelUtil.splitFM(model, ["BufferErrors_Test"])[0]
    printAndLog(f"<generateTests> Sliced model {modelPath} with BufferErrors_Test")
    printAndLog("<generateTests> Enumerating instances...(this can take a while)")
    # Make sure that the buffer error test is actually enabled
    model = featureModelUtil.addConstraints(model, ["BufferErrors_Test"])
    instances = featureModelUtil.enumerateFM(model)
    printAndLog("<generateTests> Done generating instances")

    settings = getSetting('bufferErrors')
    heapSize = parseBytes(settings['heapSize'])
    stackSize = parseBytes(settings['stackSize'])
    seed = (settings['seed'] if settings['useSeed']
                             else random.randrange(sys.maxsize))
    printAndLog(f"<generateTests> Using seed {seed}")

    tgs = [ BofTestGen(BofInstance(model, i),
                       heapSize,
                       stackSize) for i in instances ]
    rnd = random.Random(seed)

    printAndLog(f"<generateTests> Generating {settings['nTests']} tests "
                f"with seed={seed}, heap-size={heapSize}, "
                f"stack-size={stackSize}")
    if settings["nSkip"]:
        printAndLog("<generateTests> Skipping {settings['nSkip']} instances")
        for i in range(settings["nSkip"]):
            tg = rnd.choice(tgs)
            tg.genInstance(rnd, drop=True)

    for i in range(settings["nTests"]):
        # Name tests test_buffer_error_<i>.c to avoid conflicting with the
        # test_<i>.c tests in the other vulnerability classes
        out   = os.path.join(outdir, f"test_buffer_errors_{i}.c")
        outfd = ftOpenFile(out, "w")
        sys.stdout.write("\033[K")
        tg    = rnd.choice(tgs)
        outfd.write(tg.genInstance(rnd, drop=False))
        outfd.close()
    printAndLog("<generateTests> Done generating tests")

