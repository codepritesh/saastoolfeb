import functools
import logging
import os
from singleton_decorator import singleton
import traceback

@singleton
def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    dir_path = os.path.dirname(os.path.realpath(__file__))
    fh = logging.FileHandler('{}/log_err_app.log'.format(dir_path))
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    return logger


def exception_logging(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        logger = create_logger()
        try:
            return function(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            # log the exception
            err = "There was an exception in  "
            err += function.__name__
            logger.exception(err)
            print('{}___/n__{}'.format(err, tb))
            # re-raise the exception
            raise

    return wrapper
