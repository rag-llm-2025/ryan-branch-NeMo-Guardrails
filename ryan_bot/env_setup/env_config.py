from dotenv import load_dotenv
import os
from pathlib import Path

# load different .env file based on the system username
username = os.getenv('USER') or os.getenv('USERNAME')
env_file = f'.env.{username}' if username else '.env'
env_path = Path(__file__).parent / env_file
print(f'env_file: {env_file}, env_path: {env_path}')
load_dotenv(env_path)

class EnvConfig:
    # API config
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')

    # internet config
    HOST = os.getenv('HOST', '127.0.0.1')  # localhost as default
    PORT = int(os.getenv('PORT', '8000'))  # 8000 as default port

    # debug and logger config
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    PRJ_ENV = os.getenv('PRJ_ENV', 'production')  # production as default
    LOGGER_LEVEL = os.getenv('LOGGER_LEVEL', 'INFO')  # INFO as default

    # check current env configs
    @classmethod
    def show_config(cls):
        return {
            'api_key': cls.API_KEY,
            'host': cls.HOST,
            'port': cls.PORT,
            'debug': cls.DEBUG,
            'env': cls.PRJ_ENV,
            'log_level': cls.LOGGER_LEVEL
        }

print(EnvConfig.HOST)     # print HOST
print(EnvConfig.PORT)     # print PORT
print(EnvConfig.show_config())  # print all env configs