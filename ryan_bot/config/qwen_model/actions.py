from nemoguardrails.actions import action
from nemoguardrails import LLMRails, RailsConfig
from pathlib import Path
import os

from thefuzz import fuzz  # Add this import for fuzzy string matching

import logging
# Initialize logger
logger = logging.getLogger(__name__)

async def load_input_output_rails_words(config: RailsConfig, rail_words_file: str):
    try:
        # Debugging custom_data
        print(f"[RYAN_DEBUG] config.custom_data: {config.custom_data}")

        # Get path from custom_data with fallback
        path = config.custom_data.get(rail_words_file)
        if not path:
            raise ValueError("rail_words_file not configured in custom_data")

        # Convert to absolute path
        config_dir = os.path.dirname(config.config_path)
        abs_path = os.path.abspath(os.path.join(config_dir, path))

        print(f"[RYAN_DEBUG] rail_words_file path: {abs_path}")
        print(f"[RYAN_DEBUG] Path exists: {os.path.exists(abs_path)}")

        sensitive_content = []
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                sensitive_content = [line.strip() for line in f if line.strip()]
                print("[RYAN_DEBUG] rail_words_file loaded successfully. contents: ", sensitive_content)
        return sensitive_content
    except Exception as e:
        logger.error(f"[RYAN_DEBUG] Failed to load rail_words_file: {str(e)}")
        return []

@action()
async def check_sensitive_words(text: str, config: RailsConfig) -> bool:
    if not text or not isinstance(text, str):
        return False

    # 添加词库缓存
    if not hasattr(check_sensitive_words, "_word_cache"):
        check_sensitive_words._word_cache = await load_input_output_rails_words(config, "sensitive_words_file")

    # 添加模糊匹配
    text = text.lower()
    print("[RYAN_DEBUG] ============== 敏感词检查: ", text)
    has_sensitive_word = False
    for word in check_sensitive_words._word_cache:
        if len(word) > (3 * 2) and fuzz.ratio(word, text) > 80: # 模糊匹配:如果单词长度大于3的2倍,且word和text模糊匹配分数大于80, 即相似度超过80%，则认为敏感
            has_sensitive_word = True
            break
        elif word in text:
            has_sensitive_word = True
            break
    print("[RYAN_DEBUG] ============== 敏感词检查结果: ", has_sensitive_word)
    return has_sensitive_word

@action()
async def check_profanity(text: str, config: RailsConfig) -> bool:
    if not text or not isinstance(text, str):
        return False

    # 添加词库缓存
    if not hasattr(check_profanity, "_word_cache"):
        check_profanity._word_cache = await load_input_output_rails_words(config, "profanity_words_file")

    # 转换为小写进行比较
    text = text.lower()
    print(f"[RYAN_DEBUG] ============== 脏话检查: {text[:50]}...")

    # 检查是否包含脏话
    has_profanity = any(word in text for word in check_profanity._word_cache)
    print(f"[RYAN_DEBUG] ============== 脏话检查结果: {has_profanity}")

    return has_profanity

@action()
async def check_output_appropriateness(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False

    """检查输出内容是否合适"""
    # 这里可以添加更复杂的逻辑，比如调用外部API检查
    return True  # 简单实现，总是返回True