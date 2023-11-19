import time
import logging
from functools import wraps

date = time.strftime('%Y-%m-%d', time.localtime())

logging.addLevelName(2, 'SCENE')
logger = logging.getLogger('SCENE')
file_handler = logging.FileHandler(f'logs/{date}.log', 'a')
file_handler.setLevel(2)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(module)s - %(message)s'))
logger.addHandler(file_handler)
logger.setLevel(2)


def log_method(func):
    import inspect
    frame = inspect.currentframe().f_back
    caller = inspect.getmodule(frame).__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.log(2, f'{caller}.{func.__name__}({args}, {kwargs})')
        return func(*args, **kwargs)

    return wrapper


def log_class(cls):
    import inspect
    frame = inspect.currentframe().f_back
    caller = inspect.getmodule(frame).__name__
    logger.log(2, f'Caller: {caller}')
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        setattr(cls, name, log_method(method))
    return cls
