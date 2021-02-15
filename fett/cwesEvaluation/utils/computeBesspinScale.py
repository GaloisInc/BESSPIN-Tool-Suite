# Computes the BESSPIN Scale

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES

@decorate.debugWrap
def computeBesspinScale():
    """ Compute the BESSPIN scale following the document: $repo/docs/BESSPIN-Scale.pdf """
    # Will do the following:
    # 1. Read the BESSPIN coefficients values (from ./besspinCoeffs.json)
    # 2. Compute the categories scores
    # 3. Compute S(V) for each V
    # 4. Compute B

    scoresDict = getSetting("cweScores")
    warnAndLog("computeBesspinScale: This is not implemented yet.")