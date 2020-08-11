import functools
import logging


def log_assertion_fails(func):
    """decorator to log assertion errors and other errors
    catch an assertion exception from a function, log it, and the raise it
    """
    @functools.wraps(func)
    def wrappedFn(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except AssertionError as exc:
            log.exception(f"{func.__name__} failed an assertion <{exc}>")
            raise exc
        except Exception as exc:
            log.exception(f"{func.__name__} failed with non-assertion <{exc}>")
            raise exc
        return ret
    return wrappedFn


class SuiteLogger(logging.Logger):
    """AWS Test Suite Logger Configuration
    take the base logger in logging, configure it with handlers, and set log levels"""
    RESULT_LEVEL_NUM = 100
    def __init__(self, *args,
                 log_filepath="aws-test-suite.log",
                 name="aws-test-suite",
                 results_filepath="results.txt",
                 filehandler_loglevel=logging.INFO,
                 **kwargs):
        super().__init__(name, *args, **kwargs)

        # add a new log level for split filehandler
        logging.addLevelName(self.RESULT_LEVEL_NUM, "RESULTS")

        # setup file logging -- accept log level
        formatter = logging.Formatter('%(asctime)s: (%(levelname)s)  %(message)s', datefmt='%I:%M:%S %p')
        results_formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%I:%M:%S %p')

        # empty out target files
        open(log_filepath, 'w').close()
        open(results_filepath, 'w').close()

        # setup file logging
        self.filehandler = logging.FileHandler(log_filepath)
        self.filehandler.setFormatter(formatter)
        self.filehandler.setLevel(filehandler_loglevel)

        # results filepath
        self.results_filehandler = logging.FileHandler(results_filepath)
        self.results_filehandler.setFormatter(results_formatter)
        self.results_filehandler.setLevel(self.RESULT_LEVEL_NUM)

        # setup console logging -- set to info log level
        self.streamhandler = logging.StreamHandler()
        self.streamhandler.setFormatter(formatter)
        self.streamhandler.setLevel(logging.INFO)

        # add the two handlers to csaf logging
        self.addHandler(self.filehandler)
        self.addHandler(self.streamhandler)
        self.addHandler(self.results_filehandler)


    def results(self, message, *args, **kwargs):
        """new logging category -- logs to RESULTS log level and at file handle for results"""
        if self.isEnabledFor(self.RESULT_LEVEL_NUM):
            self._log(self.RESULT_LEVEL_NUM, message, args, **kwargs)


## Global Package Logger
log = SuiteLogger()

