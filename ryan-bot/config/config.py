import os
import sys

from nemoguardrails import LLMRails, RailsConfig

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_rails.qwen2.rails_init import initialize_rails

def init(llm_rails: LLMRails):
    print("================== 初始化配置 ==================")
    config = llm_rails.config
    initialize_rails(config)
    print("================== 配置初始化完成 ==================")