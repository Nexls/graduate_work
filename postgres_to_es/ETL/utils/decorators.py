import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            trying = True
            res = None
            t = start_sleep_time
            att_num = 0
            while trying:
                try:
                    res = func(*args, **kwargs)
                    trying = False
                except Exception as exc:
                    att_num += 1
                    if t > border_sleep_time:
                        logger.error(exc)
                        raise exc
                    logger.warning(f"Function '{func.__name__}' raised exception. "
                                   f'Retrying in {t} seconds. Attempt {att_num}.')
                    time.sleep(att_num)
                    t = start_sleep_time * (factor ** att_num)
            return res
        return inner
    return func_wrapper


def coroutine(func):
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        next(fn)
        return fn
    return inner
