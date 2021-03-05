# Computes the BESSPIN Scale

from fett.base.utils.misc import *
from fett.cwesEvaluation.scoreTests import SCORES, tabulate_row, prettyVulClass
from math import isclose

normalizingScoresTable = {
    SCORES.HIGH : 0.0,
    SCORES.MED : 1/3,
    SCORES.LOW : 2/3,
    SCORES.NONE : 1.0,
    SCORES.DETECTED : 1.0,
    SCORES.NOT_IMPLEMENTED : None #Intentionally a non-numerical value to cause errors if goes unnoticed
}

besspinCoeffsFactors = {
    "TI" : {"critical" : 1.0, "moderate" : 2/3, "limited" : 1/3},
    "AV" : {"user" : 1.0, "supervisor" : 2/3, "machine" : 1/3},
    "BI" : {"high" : 0.5, "low" : 1/6},
    "LDX" : {"high" : 0.5, "low" : 1/6},
}

vulClassesExceptions = {
    "PPAC" : { "osImage" : ["FreeRTOS"], "target" : ["vcu118", "qemu", "awsf1"] },
    "injection" : { "osImage" : ["FreeRTOS"], "target" : ["qemu"] }
}

# SANITY LIMITS
minBeta = 1/27 #1/(3^3)
maxBeta = 1.0

@decorate.debugWrap
def isVulClassException(vulClass):
    if (vulClass not in vulClassesExceptions):
        return False
    for xSetting,excValues in vulClassesExceptions[vulClass].items():
        if (getSetting(xSetting) not in excValues):
            return False
    return True #passed all checks

@decorate.debugWrap
def computeBesspinScale():
    """ Compute the BESSPIN scale following the document: $repo/docs/BESSPIN-Scale.pdf """
    # Will do the following:
    # 1. Compute the BESSPIN coefficients values (from ./besspinCoeffs.json)
    # 2. Compute the categories scores
    # 3. Compute S(V) for each V
    # 4. Compute B

    # Normalize the scores 
    scoresDict = getSetting("cweScores")
    normalizedScores = {vulClass:{} for vulClass in getSetting("vulClasses")}
    for vulClass in getSetting("vulClasses"):
        for cwe,cweScore in scoresDict[vulClass].items():
            if (cweScore not in normalizingScoresTable):
                errorAndLog(f"computeBesspinScale: CWE-{cwe} score is {cweScore}. "
                    f"Cannot compute the scale for scores not in [{','.join([str(s) for s in normalizingScoresTable])}]")
                return
            normalizedScores[vulClass][cwe] = normalizingScoresTable[cweScore]

    # Computations
    besspinCoeffs = safeLoadJsonFile(getSetting('besspinCoeffs'))
    vulClassesScores = {vulClass:{} for vulClass in besspinCoeffs.keys() if not vulClass.startswith('_')}
    B_SigSigBS = 0 # B numerator
    B_SigSigB = 0 # B denominator
    for vulClass in getSetting("vulClasses"):
        if (isVulClassException(vulClass)):
            continue
        vulClassesScores[vulClass]["sigma(beta(C))"] = 0
        vulClassesScores[vulClass]["sigma(beta(C)*S(C))"] = 0
        for category,cData in besspinCoeffs[vulClass].items():
            # category score
            try:
                cScore = []
                for cwe in cData["cwes"]:
                    if (cwe not in normalizedScores[vulClass]):
                        cweInfo = getSettingDict(vulClass,["testsInfo",f"test_{cwe}"])
                        if (("besspinScaleException" in cweInfo) and (getSetting("osImage") in cweInfo["besspinScaleException"])):
                            printAndLog(f"computeBesspinScale: CWE-{cwe} not found, but it is an exception. Skipping.",
                                doPrint=False)
                            continue
                        raise Exception(f"CWE-{cwe} score not found.")
                    if (normalizedScores[vulClass][cwe] is None): #skip it
                        continue
                    cScore.append(normalizedScores[vulClass][cwe])
                if (len(cScore) == 0):
                    raise Exception(f"No CWEs scores are found.")
                besspinCoeffs[vulClass][category]["S(C)"] = sum(cScore) / len(cScore)
            except Exception as exc:
                errorAndLog(f"computeBesspinScale: Failed to compute <S({category})> in <{vulClass}>.",exc=exc)
                return

            # category besspin coefficient (beta)
            try:
                ti = besspinCoeffsFactors["TI"][cData["factors"]["TI"]]
                av = besspinCoeffsFactors["AV"][cData["factors"]["AV"]]
                bi = besspinCoeffsFactors["BI"][cData["factors"]["ENV"]["BI"]]
                ldx = besspinCoeffsFactors["LDX"][cData["factors"]["ENV"]["LDX"]]
                beta = ti*av*(bi+ldx)
                if ( ((beta<minBeta) and (not isclose(beta,minBeta))) 
                    or ((beta>maxBeta) and (not isclose(beta,maxBeta))) ): #give an exception for float math imprecisions
                    raise Exception(f"Value <{beta}> out of range [{minBeta}-{maxBeta}].")
            except Exception as exc:
                errorAndLog(f"computeBesspinScale: Failed to compute <Beta({category})> in <{vulClass}>.",exc=exc)
                return
            # beta*score
            besspinCoeffs[vulClass][category]["beta(C)"] = beta
            besspinCoeffs[vulClass][category]["beta(C)*S(C)"] = beta * besspinCoeffs[vulClass][category]["S(C)"] 
            # Sigmas
            vulClassesScores[vulClass]["sigma(beta(C))"] += besspinCoeffs[vulClass][category]["beta(C)"]
            vulClassesScores[vulClass]["sigma(beta(C)*S(C))"] += besspinCoeffs[vulClass][category]["beta(C)*S(C)"]
        B_SigSigB += vulClassesScores[vulClass]["sigma(beta(C))"]
        B_SigSigBS += vulClassesScores[vulClass]["sigma(beta(C)*S(C))"]
        # S(V)
        sv = vulClassesScores[vulClass]["sigma(beta(C)*S(C))"] / vulClassesScores[vulClass]["sigma(beta(C))"]
        if ((sv<0) or (sv>1)):
            errorAndLog(f"computeBesspinScale: Failed to compute <S({vulClass})>. Value <{sv}> out of range [0,1].")
            return
        vulClassesScores[vulClass]["S(V)"] = sv
    #BESSPIN Scale: B
    B = B_SigSigBS / B_SigSigB
    if ((B<0) or (B>1)):
        errorAndLog(f"computeBesspinScale: Failed to compute the BESSPIN Scale. Value <{B}> out of range [0,1].")
        return
    # Check that the computed B is legit (i.e. all vulClasses were executed)
    for vulClass,vulClassesScore in vulClassesScores.items():
        if (isVulClassException(vulClass)):
            continue
        if ("S(V)" not in vulClassesScore):
            warnAndLog(f"computeBesspinScale: The BESSPIN Scale won't be computed since <S({vulClass})> is missing.")
            B = -1
            break

    # Display and Report
    reportFileName = os.path.join(getSetting("workDir"), "scoreReport.log")
    fScoresReport = ftOpenFile(reportFileName, 'a')
    try:
        for row in tabulate(besspinCoeffs, vulClassesScores, B):
            printAndLog(row, tee=fScoresReport)
    except Exception as exc:
        errorAndLog(f"computeBesspinScale: Failed to tabulate the results.",exc=exc)   
    fScoresReport.close()

@decorate.debugWrap
def tabulate(besspinCoeffs, vulClassesScores, B):
    nCols = 4 # vulClass | category | S(C) | S(V)
    # First, create vulClasses rows data
    rows = []
    # Add column Headers
    rows.append([["Vul. Class","Category","C(S)","V(S)"]])
    for vulClass in getSetting("vulClasses"):
        if (isVulClassException(vulClass)):
            continue
        vRows = []
        for category,cData in besspinCoeffs[vulClass].items():
            vRows.append(["",cData["name"],disp(cData["S(C)"]),""])
        # add vulClass info in the middle row
        iMidRow = len(vRows)//2
        vRows[iMidRow][0] = prettyVulClass(vulClass)
        vRows[iMidRow][-1] = disp(vulClassesScores[vulClass]["S(V)"])
        rows.append(vRows)

    # Get the widthCols
    allWidths = []
    for vRows in rows:
        allWidths += [[len(cell) for cell in row] for row in vRows]
    widthCols = [ 2 + max([w[i] for w in allWidths]) for i in range(nCols) ]
    
    # Let's create the table
    table = []
    table.append(tabulate_row([],widthCols,drawLine=True))
    for vRows in rows:
        for row in vRows:
            if (row==vRows[-1]): # last row in vRows
                customSeparations = [True]*4
                horizSeparator = '='
            else:
                customSeparations = [False,True,True,False]
                horizSeparator = '-'
            table.append(tabulate_row(row,widthCols,customSeparations=customSeparations))
            if not ((vRows==rows[-1]) and (row==vRows[-1])): # Don't draw the last line
                table.append(tabulate_row([],widthCols,drawSeparation=True,
                                customSeparations=customSeparations,horizSeparator=horizSeparator))
    # The BESSPIN Scale row
    if (B!=-1):
        bRow = ["BESSPIN Scale",disp(B) + " SSITH"]
        bWidthCols = [sum(widthCols[:2])+1,sum(widthCols[2:])+1]
        table.append(tabulate_row([],bWidthCols,drawSeparation=True,horizSeparator='='))
        table.append(tabulate_row(bRow,bWidthCols))

    table.append(tabulate_row([],widthCols,drawLine=True))
    return table

def disp(val):
    return f"{100*val:.2f}%"
