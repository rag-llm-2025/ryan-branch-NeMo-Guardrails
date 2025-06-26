import os
import sys

from nemoguardrails import LLMRails, RailsConfig

from ryan_bot.model_rails.qwen2 import initialize_rails  # 使用绝对导入

def init(llm_rails: LLMRails):
    print("================== 初始化配置 ==================")
    config = llm_rails.config
    initialize_rails(config)
    print("================== 配置初始化完成 ==================")