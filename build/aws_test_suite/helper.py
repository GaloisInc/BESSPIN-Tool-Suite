import logging


def print(message=None, level='Info'):
    """
    Prints message to console with the specified level and outputs to log accordingly

    :param message: Message to print
    :type message: str

    :param level: Level of message
    :type level: str
    """

    if message is None:
        pass

    levels = ['Critical', 'Debug', 'Error', 'Info', 'Warning']

    assert level in levels, f'{ level } is not a valid level, must be one of Critical, Debug, Error, Info, Warning'

    print(f'({level})~ {message}')

    command = level.lower()
    exec(f'logging.{command}("{message}")')