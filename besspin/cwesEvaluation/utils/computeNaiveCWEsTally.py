# Computes the naive CWEs tally scores and table

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.scoreTests import VUL_CLASSES, SCORES, tabulate_row, prettyVulClass
from besspin.cwesEvaluation.utils.computeBesspinScale import isVulClassException, disp, normalizingScoresTable

def toValue(score):
    return int(score in [SCORES.NONE, SCORES.DETECTED])

@classmethod
def normalizeToComputation (cls, score):
    """
    Translate the exact normalized and string for the table to the computation values
    """

@decorate.debugWrap
def computeNaiveCWEsTally():
    """
    Compute the Naive CWEs tally scores following the document: $repo/docs/cwesEvaluation/besspinPhilosophy.md

    SIDE-EFFECTS:
    -------------
        - Displays the tally scores table
        - Append <${workDir}/scoreReport.log> with the table
    """
    scoresDict = getSetting("cweScores")
    vulClassesScores = {vulClass:{} for vulClass in VUL_CLASSES}
    ovrTally = {"binary" : 0, "exact" : 0.0}
    ovrCwesCount = 0
    for vulClass in getSetting("vulClasses"):
        if (isVulClassException(vulClass)): #skip if the combination is NA
            continue
        testsInfo = getSettingDict(vulClass,["testsInfo"])
        try:
            vCwes = [xTest.split("test_")[1] for xTest in testsInfo]
        except Exception as exc:
            logAndExit(f"Failed to extract the CWEs of {vulClass} from <testsInfo>.",exc=exc,exitCode=EXIT.Dev_Bug)

        vTally = {"binary" : 0, "exact" : 0.0}
        vCwesCount = 0
        for cwe in vCwes:
            if (cwe not in scoresDict[vulClass]):
                cweInfo = getSettingDict(vulClass,["testsInfo",f"test_{cwe}"])
                if (("besspinScaleException" in cweInfo) and (getSetting("osImage") in cweInfo["besspinScaleException"])):
                    printAndLog(f"computeNaiveCWEsTally: CWE-{cwe} not found, but it is an exception. Skipping.",
                        doPrint=False)
                    continue
                if (("documentationOnly" in cweInfo) and cweInfo["documentationOnly"]):
                    continue
                errorAndLog(f"computeNaiveCWEsTally: Failed to compute the tally! CWE-{cwe} score not found in <{vulClass}>.")
                return
            cweScore = scoresDict[vulClass][cwe][0] # We use the floored value for the binary tally (also to check validity for NoImpl)
            if (cweScore not in normalizingScoresTable):
                errorAndLog(f"computeNaiveCWEsTally: CWE-{cwe} score is {cweScore}. "
                    f"Cannot compute the tally for scores not in [{','.join([str(s) for s in normalizingScoresTable])}]")
                return
            normalizedCweScore = normalizingScoresTable[cweScore]
            if (normalizedCweScore is None): #skip it -- Not implemented
                continue
            vTally["binary"] += toValue(cweScore)
            vTally["exact"] += scoresDict[vulClass][cwe][1]
            vCwesCount += 1 #Should not use len(vCwes) because some CWEs are exempt

        if (vCwesCount==0): #To avoid division by zero in what comes
            errorAndLog(f"computeNaiveCWEsTally: Failed to compute the tally! No CWEs found in <{vulClass}>.")
            return
        for tallyType in ["binary", "exact"]:
            ovrTally[tallyType] += vTally[tallyType]
        ovrCwesCount += vCwesCount

        #The vulClass score
        vScore = {}
        for tallyType in ["binary", "exact"]:
            vScore[tallyType] = vTally[tallyType] / vCwesCount
            if ((vScore[tallyType]<0) or (vScore[tallyType]>1)): # :mindblown:
                errorAndLog(f"computeNaiveCWEsTally: Failed to compute the {tallyType} tally <S({vulClass})>. "
                                f"Value <{vScoreExact}> out of range [0,1].")
                return
        vulClassesScores[vulClass] = {"tally":vTally, "total":vCwesCount, "score":vScore}

    #The overall score
    if (ovrCwesCount>0):
        ovrScore = {}
        for tallyType in ["binary", "exact"]:
            ovrScore[tallyType] = ovrTally[tallyType] / ovrCwesCount
            if ((ovrScore[tallyType]<0) or (ovrScore[tallyType]>1)): # :mindblown:
                errorAndLog(f"computeNaiveCWEsTally: Failed to compute overall {tallyType} tally. "
                                f"Value <{vScoreExact}> out of range [0,1].")
                return

    # Check whether it's ok to compute the overall score (i.e. all vulClasses were executed)
    for vulClass,vulClassesScore in vulClassesScores.items():
        if (isVulClassException(vulClass)):
            continue
        if ("score" not in vulClassesScore):
            warnAndLog(f"computeNaiveCWEsTally: The overall score won't be computed since <S({vulClass})> is missing.")
            ovrScore = {}
            break
    ovrDetails = {"tally":ovrTally, "total":ovrCwesCount, "score":ovrScore}

    # Display and Report
    reportFileName = os.path.join(getSetting("workDir"), "scoreReport.log")
    fScoresReport = ftOpenFile(reportFileName, 'a')
    try:
        for row in tabulate(vulClassesScores, ovrDetails):
            printAndLog(row, tee=fScoresReport) #printAndLog is ok in a try block because it doesn't exit in case of error
    except Exception as exc:
        errorAndLog(f"computeNaiveCWEsTally: Failed to tabulate the results.",exc=exc)   
    fScoresReport.close()

@decorate.debugWrap
def tabulate(vulClassesScores, ovrDetails):
    nCols = 6 # vulClass | Total | Bin Tally | Bin Score | Ex Tally | Ex Score
    # First, create vulClasses rows data
    rows = []
    # Add column Headers
    rows.append(["","","Bin", "Bin", "Exact", "Exact"])
    rows.append(["Vul. Class","Total","Tally", "Score", "Tally", "Score"])
    for vulClass in getSetting("vulClasses"):
        if (isVulClassException(vulClass)):
            continue
        rows.append([
            prettyVulClass(vulClass), str(vulClassesScores[vulClass]["total"]), 
            str(vulClassesScores[vulClass]["tally"]["binary"]), disp(vulClassesScores[vulClass]["score"]["binary"]),
            dispTally(vulClassesScores[vulClass]["tally"]["exact"]), disp(vulClassesScores[vulClass]["score"]["exact"])
            ])

    # Get the widthCols
    allWidths = [[len(cell) for cell in row] for row in rows]
    widthCols = [ 2 + max([w[i] for w in allWidths]) for i in range(nCols) ]

    # Let's create the table
    table = []
    table.append(tabulate_row([],widthCols,drawLine=True))
    for iRow, row in enumerate(rows):
        table.append(tabulate_row(row,widthCols))
        if (iRow not in [0, len(rows)-1]): # Don't draw the last line or the mid-header line
            horizSeparator = '=' if (row==rows[1]) else '-' # The header row
            table.append(tabulate_row([],widthCols,drawSeparation=True,horizSeparator=horizSeparator))

    #The overall score row
    if (ovrDetails["score"]):
        ovrRow = ([
            "Overall Score", str(ovrDetails["total"]),
            str(ovrDetails["tally"]["binary"]), disp(ovrDetails["score"]["binary"]),
            dispTally(ovrDetails["tally"]["exact"]), disp(ovrDetails["score"]["exact"])
            ])
        table.append(tabulate_row([],widthCols,drawSeparation=True,horizSeparator='='))
        table.append(tabulate_row(ovrRow,widthCols))

    table.append(tabulate_row([],widthCols,drawLine=True))
    return table

def dispTally(val):
    return f"{val:.2f}"