import logging
from typing import Any

from ryan_bot.env_setup.env_config import EnvConfig

# 定义颜色代码
class LogColors:
    RED = '\033[91m' # ERROR/CRITICAL
    YELLOW = '\033[93m' # INFO/WARNING
    RESET = '\033[0m'

logger = logging.getLogger("ryan_bot")
logger.setLevel(EnvConfig.RYAN_LOGGER_LEVEL)

# DEBUG/INFO/WARNING/ERROR/CRITICAL
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        if record.levelno >= logging.ERROR:
            return f"{LogColors.RED}{message}{LogColors.RESET}"
        elif record.levelno >= logging.INFO:
            return f"{LogColors.YELLOW}{message}{LogColors.RESET}"
        return message

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter(
        '[%(asctime)s.%(msecs)03d] [%(tag_name)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',  # 新增行号、文件名
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)
    logger.propagate = False  # 阻止日志传播到父logger

class RyanLog:
    @staticmethod
    def debug(tag_name: str = None, message: str = None, stacklevel: int = 2):
        """打印DEBUG级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.debug(message,
                    extra={'tag_name': tag_name or "ryan_bot"},
                    stacklevel=2)  # 新增stacklevel参数

    @staticmethod
    def info(tag_name: str = None, message: str = None, stacklevel: int = 2):
        """打印INFO级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.info(message,
                   extra={'tag_name': tag_name or "ryan_bot"},
                   stacklevel=2)  # 新增stacklevel参数

    @staticmethod
    def warning(tag_name: str = None, message: str = None, stacklevel: int = 2):
        """打印WARNING级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.warning(message,
                      extra={'tag_name': tag_name or "ryan_bot"},
                      stacklevel=2)  # 新增stacklevel参数

    @staticmethod
    def error(tag_name: str = None, message: str = None, stacklevel: int = 2):
        """打印ERROR级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.error(message,
                    extra={'tag_name': tag_name or "ryan_bot"},
                    stacklevel=2)  # 新增stacklevel参数

    @staticmethod
    def critical(tag_name: str = None, message: str = None, stacklevel: int = 2):
        """打印CRITICAL级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.critical(message,
                       extra={'tag_name': tag_name or "ryan_bot"},
                       stacklevel=stacklevel)  # 新增stacklevel参数

ryan_log = RyanLog()


from functools import wraps
import time

def log_kpi_async(func_name=None):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            ryan_log.critical("KPI", f"Enter {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000  # convert to ms
                ryan_log.critical("KPI", f"Leave {func.__name__} [latency: {elapsed:.2f}ms]")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                ryan_log.error("KPI", f"Error in {func.__name__}: {str(e)} [latency: {elapsed:.2f}ms]")
                raise
        return async_wrapper

    if callable(func_name):
        return decorator(func_name)
    return decorator

def log_kpi_sync(func_name=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ryan_log.critical("KPI", f"Enter {func.__name__}")
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                ryan_log.critical("KPI", f"Leave {func.__name__} [latency: {elapsed:.2f}ms]")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                ryan_log.error("KPI", f"Error in {func.__name__}: {str(e)} [latency: {elapsed:.2f}ms]")
                raise
        return wrapper

    if callable(func_name):
        return decorator(func_name)
    return decorator