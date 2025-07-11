from dotenv import load_dotenv
import os
from pathlib import Path
import logging
from functools import cached_property
import torch

from ryan_bot.utils.helper import yml_config_update

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
    MODEL_PATH = os.getenv('MODEL_PATH', '/home/ryan_niu/ryan/llm/Qwen2.5-7B-Instruct')
    ENGINE_NAME = os.getenv('ENGINE_NAME', 'ryan_vllm_engine')
    CHECKPOINT_PATH = os.getenv('CHECKPOINT_PATH', '')
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"  # 默认使用GPU

    # feature toggles
    STREAM = os.getenv('STREAM', 'False') == 'True'  # 是否启用流式响应
    ENABLE_VLLM = os.getenv('ENABLE_VLLM', 'False') == 'True'  # 是否启用vllm
    ENABLE_TEXT_EMBEDDING = os.getenv('ENABLE_TEXT_EMBEDDING', 'False') == 'True'  # 是否启用文本嵌入
    ENABLE_LATENCY_OPTIMIZATION = os.getenv('ENABLE_LATENCY_OPTIMIZATION', 'False') == 'True'  # 是否启用延迟优化

    # 日志级别配置
    RYAN_LOGGER_LEVEL = logging.DEBUG
    CLI_LOGGER_LEVEL = logging.INFO
    NEMO_LOGGER_LEVEL = logging.ERROR

    @classmethod
    def init_logger_levels(cls):
        """初始化所有日志级别配置"""
        import os
        os.environ['TZ'] = 'Asia/Shanghai'

        # Ryan日志级别
        cls.RYAN_LOGGER_LEVEL = cls._get_log_level('RYAN_LOGGER_LEVEL', logging.DEBUG)
        # CLI日志级别
        cls.CLI_LOGGER_LEVEL = cls._get_log_level('CLI_LOGGER_LEVEL', logging.INFO)
        # 测试日志级别
        cls.NEMO_LOGGER_LEVEL = cls._get_log_level('NEMO_LOGGER_LEVEL', logging.ERROR)

    @staticmethod
    def _get_log_level(env_var: str, default_level: int) -> int:
        """从环境变量获取日志级别"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.FATAL
        }
        level_str = os.getenv(env_var, '').upper()
        return level_map.get(level_str, default_level)

    # only for test: 用@cached_property 修饰实例方法缓存私有成员属性
    __show_config = {
        'host': HOST,
        'port': PORT,
        'debug': DEBUG,
        'env': PRJ_ENV,
        'log_level': RYAN_LOGGER_LEVEL,
        'llm_dir': LLM_DIR,
        'model_name': MODEL_NAME,
        'engine_name': ENGINE_NAME,
        'stream': STREAM,
        'enable_vllm': ENABLE_VLLM,
        'enable_text_embedding': ENABLE_TEXT_EMBEDDING,
        'enable_latency_optimization': ENABLE_LATENCY_OPTIMIZATION,
        'device': DEVICE
    }
    @cached_property
    def show_config(self):
        return self.__show_config

    @classmethod
    def show_config(cls):
        """显示当前环境配置"""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'debug': cls.DEBUG,
            'env': cls.PRJ_ENV,
            'log_level': cls.RYAN_LOGGER_LEVEL,
            'llm_dir': cls.LLM_DIR,
            'model_name': cls.MODEL_NAME,
            'engine_name': cls.ENGINE_NAME,
            'stream': cls.STREAM,
            'enable_vllm': cls.ENABLE_VLLM,
            'enable_text_embedding': cls.ENABLE_TEXT_EMBEDDING,
            'enable_latency_optimization': cls.ENABLE_LATENCY_OPTIMIZATION,
            'device': cls.DEVICE
        }

    @classmethod
    def update_yml_config(cls, yml_path):
        """更新yml配置文件"""
        yml_config_update(config_path=yml_path, engine_name=cls.ENGINE_NAME, model_name=cls.MODEL_NAME, model_path=cls.MODEL_PATH, device=cls.DEVICE, checkpoint_path=cls.CHECKPOINT_PATH)


def print_env_config():
    print(f"加载的环境文件: {env_file}")
    print("当前配置:")
    print(EnvConfig.show_config())

# 初始化日志级别
EnvConfig.init_logger_levels()

# update yml config
EnvConfig.update_yml_config("./config/qwen_model/config.yml")

# 打印配置信息
print_env_config()