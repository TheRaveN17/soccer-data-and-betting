import logging

# logging related constants
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_FILE = 'phx.log'

def get_logger(name="phoenix",
               format_string=DEFAULT_FORMAT,
               logging_file=DEFAULT_LOG_FILE,
               debug=True):
    """Obtain a new logger object.
    The `name` parameter will be the name of the logger and `format_string`
    will be the format it will use for logging. `logging_file` is a file
    where the messages will be written.
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(format_string)

    if not logger.handlers:
        # If the logger wasn't obtained another time,
        # then it shouldn't have any loggers

        if logging_file:
            file_handler = logging.FileHandler(logging_file, delay=True)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    if debug is True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger
