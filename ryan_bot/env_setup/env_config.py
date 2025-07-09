from dotenv import load_dotenv
import os
from pathlib import Path
import logging

# 根据系统用户名加载对应的.env文件
username = os.getenv('USER') or os.getenv('USERNAME')
env_file = f'.env.{username}' if username else '.env'
env_path = Path(__file__).parent / env_file
load_dotenv(env_path)

class EnvConfig:
    # API认证配置
    API_KEY = os.getenv('API_KEY', 'test_key')
    API_SECRET = os.getenv('API_SECRET', 'test_secret')

    # 网络配置
    HOST = os.getenv('HOST', '10.16.118.43')  # 默认使用指定IP
    PORT = int(os.getenv('PORT', '8000'))  # 默认8000端口

    # 开发调试配置
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    PRJ_ENV = os.getenv('PRJ_ENV', 'development')  # 默认开发环境

    # NeMo Guardrails配置
    LLM_DIR = os.getenv('LLM_DIR', '/home/ryan_niu/ryan/llm')
    MODEL_NAME = os.getenv('MODEL_NAME', 'Qwen2.5-7B-Instruct')
    ENGINE_NAME = os.getenv('ENGINE_NAME', 'ryan_vllm_engine')

    # 日志级别配置
    RYAN_LOGGER_LEVEL = logging.DEBUG
    CLI_LOGGER_LEVEL = logging.INFO
    TEST_LOGGER_LEVEL = logging.ERROR

    @classmethod
    def init_logger_levels(self):
        """初始化所有日志级别配置"""
        # Ryan日志级别
        self.RYAN_LOGGER_LEVEL = self._get_log_level('RYAN_LOGGER_LEVEL', logging.DEBUG)
        # CLI日志级别
        self.CLI_LOGGER_LEVEL = self._get_log_level('CLI_LOGGER_LEVEL', logging.INFO)
        # 测试日志级别
        self.TEST_LOGGER_LEVEL = self._get_log_level('TEST_LOGGER_LEVEL', logging.ERROR)

    @staticmethod
    def _get_log_level(env_var: str, default_level: int) -> int:
        """从环境变量获取日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'FATAL': logging.FATAL
        }
        level_str = os.getenv(env_var, '').upper()
        return level_map.get(level_str, default_level)

    @classmethod
    def show_config(self):
        """显示当前环境配置"""
        return {
            'api_key': self.API_KEY,
            'host': self.HOST,
            'port': self.PORT,
            'debug': self.DEBUG,
            'env': self.PRJ_ENV,
            'log_level': self.RYAN_LOGGER_LEVEL,
            'llm_dir': self.LLM_DIR,
            'model_name': self.MODEL_NAME,
            'engine_name': self.ENGINE_NAME
        }

def print_env_config():
    print(f"加载的环境文件: {env_file}")
    print("当前配置:")
    print(EnvConfig.show_config())

# 初始化日志级别
EnvConfig.init_logger_levels()

# 打印配置信息
print_env_config()