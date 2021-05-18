from besspin.base.utils.misc import *

class cwesEvaluationCompatibilityLayer:
    """
    This class wraps a target object and presents a cwesEvaluation interface layer
    """
    def __init__(self, target):
        """
        Construct a cwesEvaluationCompatibilityLayer.

        ARGUMENTS:
        ----------
            target : commonTarget
                Target to wrap.
        """
        self.objTarget = target
        self.osImage = getSetting("osImage")
        self.redirectOp = "&>" if isEqSetting('osImage', 'debian') else '> &'

    def __getattr__ (self,attr):
        """ Pass through undefined attributes to <target>. """
        return getattr(self.objTarget,attr)

    def __setattr__ (self,name,value):
        """ Pass through attribute writes to <target>. """
        if (name=='objTarget'): # exception for the special 'objTarget' member
            self.__dict__[name] = value
        else:
            setattr(self.objTarget, name, value)

    def typCommand(self, command): #Note that this returns the `textBack`
        """
        A simplified wrapper for <commonTarget.runCommand>.  This function
        passes <command> to <runCommand> with <exitOnError> set to <False>.
        This function blocks until the command returns.

        ARGUMENTS:
        ----------
            command : String
                The command to execute on the target.

        SIDE-EFFECTS:
        -------------
            - Executes <command> on the target.

        RETURNS:
        --------
            A string containing the all text returned back from the target
            during command execution.
        """
        return self.runCommand(command,exitOnError=False)[1]

    def executeTest (self,binTest):
        """
        A basic test runner for single part, non-interactive tests.
        Vulnerability classes that contain tests with multiple parts or that
        interact with the test at runtime should override this function.

        ARGUMENTS:
        ----------
            binTest : String
                Test binary to execute.

        SIDE-EFFECTS:
        -------------
            - Executes <binTest> on the target.

        RETURNS:
        --------
            A string containing test log output.
        """
        if (self.vulClass not in ["hardwareSoC"]): #list of exceptions
            self.terminateAndExit (f"<executeTest> is not implemented for <{self.vulClass}>.",exitCode=EXIT.Dev_Bug)
        
        outLog = ''
        try:
            testName = binTest.split('.')[0]
        except Exception as exc:
            self.terminateAndExit (f"executeTest: Failed to parse <{binTest}>.",exc=exc,exitCode=EXIT.Dev_Bug)

        outLog = "\n" + '*'*30 + f" {testName.upper().replace('_',' ')} " + '*'*30 + "\n\n"

        return outLog
