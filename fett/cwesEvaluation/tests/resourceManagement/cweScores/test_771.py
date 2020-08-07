from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_771 (logTest,testsDir):
    testNum = 771
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<f_not_freed>", "<g_input_param_empty_string>",testNum=testNum)
        part02 = partitionLines(testLines,"<g_input_param_empty_string>", "<g_input_param_space>",testNum=testNum)
        part03 = partitionLines(testLines,"<g_input_param_space>", "<g_first_input_param>",testNum=testNum)
        part04 = partitionLines(testLines,"<g_first_input_param>", "<g_second_input_param>",testNum=testNum)
        part05 = partitionLines(testLines,"<g_second_input_param>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(part01,"<F_MALLOC_SUCCEEDED>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02,"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02,"<POINTER_IS_NULL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part03,"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part03,"<POINTER_IS_NULL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part04,"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part04,"<POINTER_IS_NULL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part05,"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part05,"<POINTER_IS_NULL>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL


    elif (osImage == 'FreeRTOS'):
        nParts = 5
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<F_MALLOC_SUCCEEDED>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.NONE
        if (doesKeywordExist(partsLines[2],"<POINTER_IS_NULL>")):
            partsScores[2] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[2],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[2] = SCORES.V_HIGH
        else:
            partsScores[2] = SCORES.HIGH

        if (doesKeywordExist(partsLines[3],"<POINTER_IS_NULL>")):
            partsScores[3] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[3],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[3] = SCORES.V_HIGH
        else:
            partsScores[3] = SCORES.HIGH

        if (doesKeywordExist(partsLines[4],"<POINTER_IS_NULL>")):
            partsScores[4] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[4],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[4] = SCORES.V_HIGH
        else:
            partsScores[4] = SCORES.HIGH

        if (doesKeywordExist(partsLines[5],"<POINTER_IS_NULL>")):
            partsScores[5] = SCORES.V_HIGH
        elif(doesKeywordExist(partsLines[5],"<FREE_WAS_NOT_TRAPPED>")):
            partsScores[5] = SCORES.V_HIGH
        else:
            partsScores[5] = SCORES.HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore ([],testNum)

    listScores = [adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (listScores ,testNum)