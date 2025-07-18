from nemoguardrails.actions import action
from nemoguardrails import LLMRails, RailsConfig
from pathlib import Path
import os
import datetime
from thefuzz import fuzz  # Add this import for fuzzy string matching

from nemoguardrails.ryan_logger import ryan_log

tag_name="qwen_model.actions.py"

async def load_input_output_rails_words(config: RailsConfig, rail_words_file: str):
    try:
        # Debugging custom_data
        ryan_log.debug(tag_name, f"config.custom_data: {config.custom_data}")

        # Get path from custom_data with fallback
        path = config.custom_data.get(rail_words_file)
        if not path:
            raise ValueError("rail_words_file not configured in custom_data")

        # Convert to absolute path
        config_dir = os.path.dirname(config.config_path)
        abs_path = os.path.abspath(os.path.join(config_dir, path))
        ryan_log.debug(tag_name, f"rail_words_file path: {abs_path}")
        ryan_log.debug(tag_name, f"Path exists: {os.path.exists(abs_path)}")

        sensitive_content = []
        if os.path.exists(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f:
                sensitive_content = [line.strip() for line in f if line.strip()]
                ryan_log.debug(tag_name, f"rail_words_file loaded successfully. contents: {sensitive_content}")
        return sensitive_content
    except Exception as e:
        ryan_log.error(tag_name, f"Failed to load rail_words_file: {str(e)}")
        return []

@action()
async def check_sensitive_words(text: str, config: RailsConfig) -> bool:
    if not text or not isinstance(text, str):
        return False

    # add sensitive words cache
    if not hasattr(check_sensitive_words, "_word_cache"):
        check_sensitive_words._word_cache = await load_input_output_rails_words(config, "sensitive_words_file")

    # add fuzzy matching and check for sensitive words
    text = text.lower()
    ryan_log.info(tag_name, f"敏感词检查: {text}")
    has_sensitive_word = False
    for word in check_sensitive_words._word_cache:
        # fuzzy matching: if the length of the word is greater than twice the length of 3,
        # and the fuzzy matching score between word and text is greater than 80,
        # that is to say, the similarity is more than 80%, it is considered sensitive
        if len(word) > (3 * 2) and fuzz.ratio(word, text) > 80:
            has_sensitive_word = True
            break
        elif word in text:
            has_sensitive_word = True
            break
    ryan_log.info(tag_name, f"敏感词检查结果: {has_sensitive_word}")
    return has_sensitive_word

@action()
async def check_profanity(text: str, config: RailsConfig) -> bool:
    if not text or not isinstance(text, str):
        return False

    # add profanity words cache
    if not hasattr(check_profanity, "_word_cache"):
        check_profanity._word_cache = await load_input_output_rails_words(config, "profanity_words_file")

    # convert to lower case for profanity words check
    text = text.lower()
    ryan_log.info(tag_name, f"脏话检查: {text[:50]}...")

    # check profanity words
    has_profanity = any(word in text for word in check_profanity._word_cache)
    ryan_log.info(tag_name, f"脏话检查结果: {has_profanity}")

    return has_profanity

@action()
async def check_output_appropriateness(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False

    """check if the output is appropriate"""
    # TODO: add compliance check for output appropriateness, such as using an external API to check the content for profanity
    return True

@action()
async def get_product_price(product_name: str):
    # TODO: add logic to get product price from an external API or database
    return "100"

@action()
async def get_weather(text: str):
    # 这里可以调用第三方天气API，例如:
    # weather_data = await call_weather_api(location=text)
    # return f"今天{weather_data['location']}的天气是{weather_data['forecast']}"
    return "今天天气晴朗"  # 目前是模拟数据，实际应用中需要替换为API调用结果

@action()
async def get_current_time(text: str):
    return "现在时间是" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")