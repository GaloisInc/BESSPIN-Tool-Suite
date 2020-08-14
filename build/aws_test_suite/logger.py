import functools
from termcolor import cprint
from datetime import datetime


def log_assertion_fails(func):
    """decorator to log assertion errors and other errors
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

        if message is None:
            pass

        levels = {
            "Debug": "yellow",
            "Error": "red",
            "Info": "white",
            "Warning": "yellow",
            "Results": "cyan",
        }

        # Check log level in levels.
        assert level in list(
            levels.keys()
        ), f"{level} is not a valid level, must be one of {', '.join(levels.keys())}"

        # Print all but debug (to file) and info (to default color) to screen
        if level.lower() != "debug" and level.lower() != "info":
            # Print to screen in color
            cprint(f"({level})~ {message}", levels[level])

        if level.lower() == "info":
            print(f"({level})~ {message}")

        # Write results to results file
        if level.lower() == "results":
            with open(self.results_fname, "a") as f:
                f.write(f"[ { datetime.now().strftime('%Y/%m/%d') } ] : { message }\n")

        # Write log message
        with open(self.log_fname, "a") as f:
            f.write(
                f"[ { datetime.now().strftime('%Y/%m/%d @ %H:%M:%S:%f') } ] : ({level})~ {message}\n"
            )

        if level.lower() == "error":
            cprint("(Error)~ Exiting.", "red")
            exit(0)

    def debug(self, message):
        self.log_out(message, "Debug")

    def error(self, message):
        self.log_out(message, "Error")

    def info(self, message):
        self.log_out(message, "Info")

    def warning(self, message):
        self.log_out(message, "Warning")

    def results(self, message):
        self.log_out(message, "Results")


## Global Package Logger
log = Logger()

