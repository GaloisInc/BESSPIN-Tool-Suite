from termcolor import cprint
from datetime import datetime


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
        ), f"{level} is not a valid level, must be one of Critical, Debug, Error, Info, Warning"

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


log = Logger()


# log.info("This is a test info")
# log.debug("This is a test debug")
# log.warning("This is a test warning")
# log.error("This is a test error")
