import logging
from typing import Any

logger = logging.getLogger("ryan_bot")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s.%(msecs)03d] [%(tag_name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)

class RyanLog:
    @staticmethod
    def debug(tag_name: str = None, message: str = None):
        """打印DEBUG级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.debug(message, extra={'tag_name': tag_name or "ryan_bot"})

    @staticmethod
    def info(tag_name: str = None, message: str = None):
        """打印INFO级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.info(message, extra={'tag_name': tag_name or "ryan_bot"})

    @staticmethod
    def warning(tag_name: str = None, message: str = None):
        """打印WARNING级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.warning(message, extra={'tag_name': tag_name or "ryan_bot"})

    @staticmethod
    def error(tag_name: str = None, message: str = None):
        """打印ERROR级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.error(message, extra={'tag_name': tag_name or "ryan_bot"})

    @staticmethod
    def critical(tag_name: str = None, message: str = None):
        """打印CRITICAL级别日志"""
        if message is None and tag_name is not None:
            message, tag_name = tag_name, "ryan_bot"
        logger.critical(message, extra={'tag_name': tag_name or "ryan_bot"})

ryan_log = RyanLog()