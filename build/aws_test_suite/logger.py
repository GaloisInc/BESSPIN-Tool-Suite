import functools
from termcolor import cprint
from datetime import datetime


def log_assertion_fails(func):
    """
    decorator to log assertion errors and other errors
    catch an assertion exception from a function, log it, and the raise it
    """

    @functools.wraps(func)
    def wrappedFn(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except AssertionError as exc:
            log.error(f"{func.__name__} failed an assertion <{exc}>")
            raise exc
        except Exception as exc:
            log.error(f"{func.__name__} failed with non-assertion <{exc}>")
            raise exc
        return ret

    return wrappedFn


def debug_wrap(func):
    """
    decorator to write to log when functions are entered and exited
    """

    @functools.wraps(func)
    def wrappedFn(*args, **kwargs):
        try:
            caller = sys._getframe(1).f_code.co_name
        except:
            caller = "unknown-caller"
        log.debug(f"Entering <{func.__name__}>. [called from <{caller}>]")
        # logging.debug(f">>>> args={args}, kwargs={kwargs}") #super-duper debug
        ret = func(*args, **kwargs)
        log.debug(f"Exitting <{func.__name__}>.")
        return ret

    return wrappedFn


def format_exc(exc):
    """ format the exception for printing """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return "<Non-recognized Exception>"


class Logger:
    def __init__(self, log_fname="aws-test-suite.log", results_fname="results.txt"):
        """
        Global logger setup
        :param log_fname: Output log filename, defaults to 'aws-test-suite.log'
        :type log_fname: str, optional
        :param level: Output information level, defaults to 'info'
        :type level: str, optional
        """

        # Store the name of the log files
        self.log_fname = log_fname
        self.results_fname = results_fname

        # Define colors for certain log levels
        self.levels = {
            "Debug": "yellow",
            "Error": "red",
            "Info": None,
            "Warning": "yellow",
            "Results": "cyan",
            "Status": "green",
        }

        # Empty out log files
        open(log_fname, "w").close()
        open(results_fname, "w").close()

    def log_out(self, message=None, level="Info"):
        """
        Prints message to console with the specified level and outputs to log accordingly
        :param message: Message to print
        :type message: str
        :param level: Level of message
        :type level: str
        """

        # Do nothing with a blank message
        if message is None:
            pass

        # Check log level in levels.
        assert level in list(
            self.levels.keys()
        ), f"{level} is not a valid level, must be one of {', '.join(levels.keys())}"

        # Print all except:
        # - debug (goes to file)
        # - info (goes to screen un-colored)
        # - results (varies in color dep. on result)
        if (
            (level.lower() != "debug")
            and (level.lower() != "info")
            and (level.lower() != "results")
        ):
            # Print to screen in color
            cprint(f"({level})~ {message}", self.levels[level])

        # Print info to screen uncolored
        if level.lower() == "info":
            print(f"({level})~ {message}")

        # Write results to results file, and print in color
        if level.lower() == "results":
            # Log
            with open(self.results_fname, "a") as f:
                f.write(f"[ { datetime.now().strftime('%Y/%m/%d') } ] : { message }\n")

            if "fail" in message.lower():
                cprint(f"({level})~ {message}", self.levels["Warning"])
            else:
                cprint(f"({level})~ {message}", self.levels[level])

        # Write log message no matter what level
        with open(self.log_fname, "a") as f:
            f.write(
                f"[ { datetime.now().strftime('%Y/%m/%d @ %H:%M:%S:%f') } ] : ({level})~ {message}\n"
            )

    def debug(self, message):
        self.log_out(message, "Debug")

    def error(self, message, exc=None):
        self.log_out(message, "Error")
        if exc:
            self.log_out(format_exc(exc), "Error")
        self.log_out("Exiting.", "Error")
        exit(-1)

    def info(self, message):
        self.log_out(message, "Info")

    def warning(self, message, exc=None):
        self.log_out(message, "Warning")
        if exc:
            self.log_out(format_exc(exc), "Warning")

    def results(self, message):
        self.log_out(message, "Results")

    def status(self, message):
        self.log_out(message, "Status")


## Global Package Logger
log = Logger()
