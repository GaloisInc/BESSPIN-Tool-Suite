# Computes the naive CWEs tally scores and table

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.scoreTests import VUL_CLASSES, SCORES, tabulate_row, prettyVulClass
from besspin.cwesEvaluation.utils.computeBesspinScale import isVulClassException, disp

def toValue(score):
    return int(score in [SCORES.NONE, SCORES.DETECTED])

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
    ovrTally = 0
    ovrCwesCount = 0
    for vulClass in getSetting("vulClasses"):
        if (isVulClassException(vulClass)): #skip if the combination is NA
            continue
        testsInfo = getSettingDict(vulClass,["testsInfo"])
        try:
            vCwes = [xTest.split("test_")[1] for xTest in testsInfo]
        except Exception as exc:
            logAndExit(f"Failed to extract the CWEs of {vulClass} from <testsInfo>.",exc=exc,exitCode=EXIT.Dev_Bug)

        vTally = 0
        vCwesCount = 0
        for cwe in vCwes:
            if (cwe not in scoresDict[vulClass]):
                cweInfo = getSettingDict(vulClass,["testsInfo",f"test_{cwe}"])
                if (("besspinScaleException" in cweInfo) and (getSetting("osImage") in cweInfo["besspinScaleException"])):
                    printAndLog(f"computeNaiveCWEsTally: CWE-{cwe} not found, but it is an exception. Skipping.",
                        doPrint=False)
                    continue
                errorAndLog(f"computeNaiveCWEsTally: Failed to compute the tally! CWE-{cwe} score not found in <{vulClass}>.")
                return
            vTally += toValue(scoresDict[vulClass][cwe])
            vCwesCount += 1 #Should not use len(vCwes) because some CWEs are exempt

        if (vCwesCount==0): #To avoid division by zero in what comes
            errorAndLog(f"computeNaiveCWEsTally: Failed to compute the tally! No CWEs found in <{vulClass}>.")
            return
        ovrTally += vTally
        ovrCwesCount += vCwesCount

        #The vulClass score
        vScore = vTally / vCwesCount
        if ((vScore<0) or (vScore>1)): # :mindblown:
            errorAndLog(f"computeNaiveCWEsTally: Failed to compute <S({vulClass})>. Value <{vScore}> out of range [0,1].")
            return
        vulClassesScores[vulClass] = {"tally":vTally, "total":vCwesCount, "score":vScore}

    #The overall score
    ovrScore = ovrTally / ovrCwesCount
    if ((ovrScore<0) or (ovrScore>1)): # :mindblown:
        errorAndLog(f"computeNaiveCWEsTally: Failed to compute the overall score. Value <{ovrScore}> out of range [0,1].")
        return

    # Check whether it's ok to compute the overall score (i.e. all vulClasses were executed)
    for vulClass,vulClassesScore in vulClassesScores.items():
        if (isVulClassException(vulClass)):
            continue
        if ("score" not in vulClassesScore):
            warnAndLog(f"computeNaiveCWEsTally: The overall score won't be computed since <S({vulClass})> is missing.")
            ovrScore = -1
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
    nCols = 4 # vulClass | Tally | Total | Score
    # First, create vulClasses rows data
    rows = []
    # Add column Headers
    rows.append(["Vul. Class","Tally","Total","Score"])
    for vulClass in getSetting("vulClasses"):
        if (isVulClassException(vulClass)):
            continue
        rows.append([prettyVulClass(vulClass), str(vulClassesScores[vulClass]["tally"]),
                        str(vulClassesScores[vulClass]["total"]), disp(vulClassesScores[vulClass]["score"])])

    # Get the widthCols
    allWidths = [[len(cell) for cell in row] for row in rows]
    widthCols = [ 2 + max([w[i] for w in allWidths]) for i in range(nCols) ]

    # Let's create the table
    table = []
    table.append(tabulate_row([],widthCols,drawLine=True))
    for row in rows:
        table.append(tabulate_row(row,widthCols))
        if (row!=rows[-1]): # Don't draw the last line
            horizSeparator = '=' if (row==rows[0]) else '-' # The header row
            table.append(tabulate_row([],widthCols,drawSeparation=True,horizSeparator=horizSeparator))

    #The overall score row
    if (ovrDetails["score"]!=-1):
        ovrRow = (["Overall Score",str(ovrDetails["tally"]),
                    str(ovrDetails["total"]),disp(ovrDetails["score"])])
        table.append(tabulate_row([],widthCols,drawSeparation=True,horizSeparator='='))
        table.append(tabulate_row(ovrRow,widthCols))

    table.append(tabulate_row([],widthCols,drawLine=True))
    return table