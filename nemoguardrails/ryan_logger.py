import logging
from typing import Any, Optional

from ryan_bot.env_setup.env_config import EnvConfig

class LogColors:
    RED = '\033[91m'  # ERROR/CRITICAL
    YELLOW = '\033[93m'  # INFO/WARNING
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
    def _log(
        level: str,
        tag_name: Optional[str] = None,
        message: Optional[str] = None,
        *args,
        stacklevel: int = 3,
        **kwargs
    ):
        if message is None and tag_name is not None:
            if isinstance(tag_name, str) and not args and 'stacklevel' not in kwargs:
                message, tag_name = tag_name, "ryan_bot"
            else:
                message = tag_name
                tag_name = "ryan_bot"

        # if args:
        #     message = str(message) + "".join(str(arg) for arg in args)
        # 支持格式化字符串参数
        if args:
            message = message % args if isinstance(message, str) else str(message)

        getattr(logger, level)(
            message,
            extra={'tag_name': tag_name or "ryan_bot"},
            stacklevel=stacklevel
        )

    @staticmethod
    def debug(tag_name=None, message=None, *args, **kwargs):
        RyanLog._log('debug', tag_name, message, *args, **kwargs)

    @staticmethod
    def info(tag_name=None, message=None, *args, **kwargs):
        RyanLog._log('info', tag_name, message, *args, **kwargs)

    @staticmethod
    def warning(tag_name=None, message=None, *args, **kwargs):
        RyanLog._log('warning', tag_name, message, *args, **kwargs)

    @staticmethod
    def error(tag_name=None, message=None, *args, **kwargs):
        RyanLog._log('error', tag_name, message, *args, **kwargs)

    @staticmethod
    def critical(tag_name=None, message=None, *args, **kwargs):
        RyanLog._log('critical', tag_name, message, *args, **kwargs)

ryan_log = RyanLog()


from functools import wraps
import asyncio  # 添加这行导入
import time
def _log_kpi_decorator(is_async: bool):
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            ryan_log.critical("KPI", f"Enter {func.__name__}")
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                ryan_log.critical("KPI", f"Leave {func.__name__} [latency: {elapsed:.2f}ms]", stacklevel = 4)
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                ryan_log.error("KPI", f"Error in {func.__name__}: {str(e)} [latency: {elapsed:.2f}ms]", stacklevel = 4)
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            ryan_log.critical("KPI", f"Enter {func.__name__}", stacklevel = 4)
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                ryan_log.critical("KPI", f"Leave {func.__name__} [latency: {elapsed:.2f}ms]", stacklevel = 4)
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                ryan_log.error("KPI", f"Error in {func.__name__}: {str(e)} [latency: {elapsed:.2f}ms]", stacklevel = 4)
                raise

        return async_wrapper if is_async else sync_wrapper
    return decorator

def log_kpi_async(func=None):
    decorator = _log_kpi_decorator(is_async=True)
    return decorator(func) if callable(func) else decorator

def log_kpi_sync(func=None):
    decorator = _log_kpi_decorator(is_async=False)
    return decorator(func) if callable(func) else decorator