from termcolor import cprint
from datetime import datetime


class Logger:
    def __init__(self, log_fname="aws-test-suite.log"):
        """
        Global logger setup

        :param log_fname: Output log filename, defaults to 'aws-test-suite.log'
        :type log_fname: str, optional

        :param level: Output information level, defaults to 'info'
        :type level: str, optional
        """

        # Store the name of the log file
        self.log_fname = log_fname

        # Empty out log file
        open(log_fname, "w").close()

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
            "Info": "cyan",
            "Warning": "yellow",
        }

        # Check log level in levels.
        assert level in list(
            levels.keys()
        ), f"{level} is not a valid level, must be one of Critical, Debug, Error, Info, Warning"

        # Print all but debug to screen
        if level.lower() != "debug":
            # Print to screen in color
            cprint(f"({level})~ {message}", levels[level])

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


log = Logger()


# log.info("This is a test info")
# log.debug("This is a test debug")
# log.warning("This is a test warning")
# log.error("This is a test error")
