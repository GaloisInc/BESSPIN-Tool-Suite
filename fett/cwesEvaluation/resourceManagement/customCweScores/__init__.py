import glob, os
__all__ = []
for pyFile in glob.glob(os.path.join(os.path.dirname(__file__), "*.py")):
	if (os.path.isfile(pyFile)) and (not pyFile.endswith('__init__.py')):
		__all__.append(os.path.basename(pyFile)[:-3])

from fett.cwesEvaluation.resourceManagement.customCweScores import *
del glob
del os
