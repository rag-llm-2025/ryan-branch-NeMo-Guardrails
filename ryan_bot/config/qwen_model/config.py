from ryan_bot.config.qwen_model.actions import check_sensitive_words, check_profanity, check_output_appropriateness
from nemoguardrails import LLMRails, RailsConfig
from ryan_bot.model_rails.qwen2 import initialize_rails
from ryan_bot.utils.ryan_logger import ryan_log
import os

tag_name = "qwen_model.config.py"

def init(llm_rails: LLMRails):
    rails_dir = os.path.join(os.path.dirname(__file__), "rails")
    ryan_log.debug(tag_name, f"Rails目录绝对路径: {rails_dir}")

    # ryan_log.debug(tag_name, f"Rails文件内容:")
    # for file in os.listdir(rails_dir):
    #     ryan_log.debug(tag_name, f"=== {file} ===")
    #     with open(os.path.join(rails_dir, file), 'r') as f:
    #         ryan_log.debug(tag_name, f.read())

    # init model and guardrails
    ryan_log.info(tag_name, f"================== 初始化配置 ==================")
    config = llm_rails.config
    initialize_rails(config)

    # register custom actions
    ryan_log.debug(tag_name, f"注册自定义动作: check_sensitive_words")
    llm_rails.register_action(
        action=check_sensitive_words,
        name="check_sensitive_words"
    )

    ryan_log.debug(tag_name, f"注册自定义动作: check_profanity")
    llm_rails.register_action(
        action=check_profanity,
        name="check_profanity"
    )

    ryan_log.debug(tag_name, f"注册自定义动作: check_output_appropriateness")
    llm_rails.register_action(
        action=check_output_appropriateness,
        name="check_output_appropriateness"
    )

    ryan_log.info(tag_name, f"================== 配置完成 ==================")
