from fett.cwesEvaluation.injection.customCweScores.controlFlowTest import scoreControlFlowTest

def test_inj_3 (logLines):
    return scoreControlFlowTest(logLines, "INJ-3")
