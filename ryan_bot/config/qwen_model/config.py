from ryan_bot.config.qwen_model.actions import check_sensitive_words, check_profanity, check_output_appropriateness

from nemoguardrails import LLMRails, RailsConfig

from ryan_bot.model_rails.qwen2 import initialize_rails  # 使用绝对导入

import os

def init(llm_rails: LLMRails):

    # 添加调试语句
    # rails_dir = os.path.join(os.path.dirname(__file__), "rails")
    # print("[DEBUG] Rails files:", os.listdir(rails_dir))

    # 添加详细调试信息
    rails_dir = os.path.join(os.path.dirname(__file__), "rails")
    print("[DEBUG] Rails目录绝对路径:", rails_dir)
    # print("[DEBUG] Rails文件内容:")
    # for file in os.listdir(rails_dir):
    #     print(f"=== {file} ===")
    #     with open(os.path.join(rails_dir, file), 'r') as f:
    #         print(f.read())


    print("================== 初始化配置 ==================")
    config = llm_rails.config

    initialize_rails(config)
    print("[RYAN_DEBUG] Config paths:", config.rails.input.flows)

    # 注册自定义动作
    llm_rails.register_action(
        action=check_sensitive_words,
        name="check_sensitive_words"
    )
    llm_rails.register_action(
        action=check_profanity,
        name="check_profanity"
    )
    llm_rails.register_action(
        action=check_output_appropriateness,
        name="check_output_appropriateness"
    )
    print("================== 配置初始化完成 ==================")