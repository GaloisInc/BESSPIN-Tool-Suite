import logging
from termcolor import cprint


class Logger:
    def __init__(self, log_fname="aws-test-suite.log", level="info"):
        """
        Global logger setup

        :param log_fname: Output log filename, defaults to 'aws-test-suite.log'
        :type log_fname: str, optional

        :param level: Output information level, defaults to 'info'
        :type level: str, optional
        """

        # empty out log file
        open(log_fname, "w").close()
        llevel = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "notset": logging.NOTSET,
        }
        log_level = llevel[level]
        logging.basicConfig(
            format="%(asctime)s: (%(levelname)s)~  %(message)s",
            datefmt="%I:%M:%S %p",
            level=log_level,
            handlers=[logging.FileHandler(log_fname)],
        )
        logging.info(
            f"AWS Test Suite Logger Initialized\nLog File: {log_fname}\nLog Level: {level}"
        )

    def log(self, message=None, level="Info"):
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
            "Critical": "red",
            "Debug": "yellow",
            "Error": "red",
            "Info": "cyan",
            "Warning": "yellow",
        }

        assert level in list(
            levels.keys()
        ), f"{level} is not a valid level, must be one of Critical, Debug, Error, Info, Warning"

        # print(f"({level})~ {message}"
        cprint(f"({level})~ {message}", levels[level])

        command = level.lower()
        exec(f'logging.{command}("{message}")')

        if command == "error":
            print("(Error)~ Exiting.")
            exit(0)


console = Logger()
