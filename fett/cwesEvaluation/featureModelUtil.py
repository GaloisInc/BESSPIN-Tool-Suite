import json
import subprocess
import tempfile
import copy
import os
import sys

from fett.base.utils.misc import *

def makeFMJSONCstr(f):
    return { 'kind' : 'feat',
             'name' : f }

def makeClaferCstr(f):
    return f"[ {f} ]"

def tryCheckOutput(cmd):
    cmdstr = " ".join(cmd)
    try:
        return subprocess.check_output(cmd,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        errorstr = e.output.decode('utf-8')
        logAndExit(f"<featureModelUtil> <{cmdstr}> returned non-zero exit "
                   f"code with output: {errorstr}",
                   exc=e)
    except Exception as e:
        logAndExit(f"<featureModelUtil> Error running command <{cmdstr}>",
                   exc=e)

def tryCheckJSON(cmd):
    r = tryCheckOutput(cmd)
    try:
        return json.loads(r)
    except Exception as exc:
        logAndExit(f"<featureModelUtil> Unexpected or malformed JSON from <{cmd}>",
                   exc=exc)

def claferOfFM(fm):
    """
    computes the pipeline: cat fm | besspin-feature-model-tool print-clafer
    """
    tmpfmjson = tempfile.NamedTemporaryFile(mode='w', suffix='.fm.json', delete=True)
    json.dump(fm, tmpfmjson)
    tmpfmjson.flush()

    cmd = ["besspin-feature-model-tool", "print-clafer", tmpfmjson.name]
    out = tryCheckOutput(cmd)
    return out

def addConstraints(fm, cs):
    fm = copy.deepcopy(fm)
    for c in cs:
        fm['constraints'].append(makeFMJSONCstr(c))
    return fm

def dumpJSONToTemp(v,delete=True):
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=delete)
    try:
        json.dump(v, temp)
    except Exception as exc:
        logAndExit(f"<featureModelUtil> failed to dump {v} as json to {temp.name}",
                   exc=exc)
    temp.flush()
    return temp

def checkMust(fm, cs):
    temp = dumpJSONToTemp(fm)
    cmd = ["besspin-feature-model-tool", "check-req", temp.name] + cs
    r = tryCheckJSON(cmd)
    temp.close()
    return r

def checkSat(fm, css):
    """
    Given css: list[list[String]], a list of features
          fm:  fmjson object
    Return list[Bool] R
      such that r[i] <=> (FM `join` CS[i] is non-empty)
    """
    fms = [ addConstraints(fm, cs) for cs in css    ]
    temp = dumpJSONToTemp(fms)
    cmd = ["besspin-feature-model-tool", "check-sat", temp.name]
    return tryCheckJSON(cmd)

def findParent(fm, f):
    p = fm['features'][f]['name']
    while p is not None:
        parent = p
        p = fm['features'][p]['parent']
    return parent

def pruneConstraints(cs, fs):
    def kill(c):
        k = (c['kind'] == 'feat' and c['name'] not in fs) or \
            (c['kind'] == 'op' and any([kill(c2) for c2 in c['args']]))
        return k
    return [c for c in cs if not kill(c)]

def pruneFeatures(features, rootFeatures):
    fs = {}
    for f in features:
        if f in rootFeatures:
            fs[f] = features[f]
    return fs

def enumerateFM(fm):
    t = dumpJSONToTemp(fm, delete=False)
    cmd = ["besspin-feature-model-tool", "all-configs", t.name]
    r = tryCheckJSON(cmd)
    t.close()
    return r

def splitFM(fm, roots=None):
    features = {}
    if roots is None:
        roots = fm['roots']
    for root in roots:
        features[root] = []

    for f in fm['features']:
        p = findParent(fm, f)
        if p in features:
            features[p].append(fm['features'][f]['name'])

    models = []
    for root in roots:
        fmForRoot = copy.deepcopy(fm)

        prunedFs = pruneFeatures(fmForRoot['features'], features[root])
        prunedCs = pruneConstraints(fmForRoot['constraints'], features[root])

        fmForRoot['roots']       = [root]
        fmForRoot['features']    = prunedFs
        fmForRoot['constraints'] = prunedCs

        models.append(fmForRoot)
    return models

def loadFM(fn):
    f, ext = os.path.splitext(fn)

    if ext == ".cfr":
        inFile = ftOpenFile(fn, "r")
        text = inFile.read()
        inFile.close()
        cmd  = ["clafer", "-s", "-o", "-m", "fmjson", fn ]
        text = tryCheckOutput(cmd)
    elif ext == ".json" and os.path.splitext(f)[1] == ".fm":
        inFile = ftOpenFile(fn, "r")
        text = inFile.read()
        inFile.close()
    else:
        raise Exception("loadfm() expects a clafer (.cfr) or fmjson (.fm.json) file")

    return json.loads(text)
