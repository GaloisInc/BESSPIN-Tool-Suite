from fett.cwesEvaluation.tests.resourceManagement.cweScores.helpers import *

def test_188 (SCORES, customScorer, logTest,testsDir):
    testNum = 188
    if (logTest != "test_{0}.log".format(testNum)):
        return ["CWE-{0}".format(testNum), "--", "Wrong test called!"]
    testLines = readLogLines(logTest,testsDir)

    osImage = getOsImage(testLines,testNum=testNum)

    if (osImage == 'debian' or osImage == 'FreeBSD'):
        nParts = 1
        partsLines = regPartitionTest (testLines,nParts,testNum=testNum)
        partsScores = {}

        part01 = partitionLines(testLines,"<example_byte_in_front>", "<example_one_byte_past>",testNum=testNum)
        part02 = partitionLines(testLines,"<example_one_byte_past>", "<example_three_bytes_in_front>",testNum=testNum)
        part03 = partitionLines(testLines,"<example_three_bytes_in_front>", "<example_three_bytes_past>",testNum=testNum)
        part04 = partitionLines(testLines,"<example_three_bytes_past>", "<example_input_args_past_on_stack>",testNum=testNum)
        part05 = partitionLines(testLines,"<example_input_args_past_on_stack>", "<example_input_args_in_front_on_stack>",testNum=testNum)
        part06 = partitionLines(testLines,"<example_input_args_in_front_on_stack>", "-"*50,testNum=testNum)

        if (doesKeywordExist(testLines,"<INVALID>")):
            partsScores[1] = SCORES.CALL_ERR
        elif (doesKeywordExist(part01,"<WRONG_PROTOCOL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part02,"<WRONG_PROTOCOL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part02,"<PROTOCOL_ONE_BYTE_PAST>")):
            partsScores[1] = SCORES.NONE
        elif (doesKeywordExist(part03,"<WRONG_PROTOCOL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (doesKeywordExist(part04,"<WRONG_PROTOCOL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part05,"<EXPECTED_INPUT_PAST>")):
            partsScores[1] = SCORES.NONE
        elif (doesKeywordExist(part05,"<WRONG_PROTOCOL>")):
            partsScores[1] = SCORES.V_HIGH
        elif (not doesKeywordExist(part06,"<EXPECTED_INPUT_PAST>")):
            partsScores[1] = SCORES.NONE
        elif (doesKeywordExist(part06,"<WRONG_PROTOCOL>")):
            partsScores[1] = SCORES.V_HIGH
        else:
            partsScores[1] = SCORES.FAIL

    elif (osImage == 'FreeRTOS'):
        nParts = 4
        partsLines = regPartitionTestFreeRTOS(testLines,nParts,testNum=testNum)
        partsScores = {}

        if (doesKeywordExist(partsLines[1],"<PROTOCOL_ONE_BYTE_IN_FRONT>")):
            partsScores[1] = SCORES.NONE
        else:
            partsScores[1] = SCORES.V_HIGH
        if (doesKeywordExist(partsLines[2],"<PROTOCOL_ONE_BYTE_PAST>")):
            partsScores[2] = SCORES.NONE
        else:
            partsScores[2] = SCORES.V_HIGH

        if (doesKeywordExist(partsLines[3],"<EXPECTED_INPUT_PAST>")):
                partsScores[3] = SCORES.NONE
        else:
            partsScores[3] = SCORES.V_HIGH

        if (doesKeywordExist(partsLines[4],"<EXPECTED_INPUT_PAST>")):
            partsScores[4] = SCORES.NONE
        else:
            partsScores[4] = SCORES.V_HIGH

    else:
        print (f"Error: parsing test_{testNum}.log is not implemented for <{osImage}>.")
        return overallScore (SCORES, [],testNum)

    listScores = [customScorer.adjustToCustomScore(partsLines[iPart],partsScores[iPart]) for iPart in range(1,nParts+1)]
    return overallScore (SCORES, listScores ,testNum)