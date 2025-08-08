import logging
from typing import Optional
import requests
import time
import os
import json
from requests.exceptions import RequestException
from nemoguardrails.logging.verbose import console

from simple_logger import RyanLogger as logger
from gpt_4o_verify import GPT4OWrapper
from generate_prompt import generate_response_prompt, generate_guardrail_prompt

# api_server address and port
RAILS_HOST = os.getenv("RAILS_HOST", "localhost")
print("RAILS_HOST:", RAILS_HOST)
API_KEY = os.getenv("OPENAI_URL_AUTH", "")

API_URL = f"http://{RAILS_HOST}:8010/generate"
HEADERS = {"Content-Type": "application/json"}
MAX_RETRIES = 3

def send_request(query: str) -> Optional[dict]:
    """发送请求到API服务器"""
    data = {
        "user_id": "test_user",
        "query": query
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url=API_URL,
                headers=HEADERS,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"request failed (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt == MAX_RETRIES - 1:
                return None

if __name__ == "__main__":
    query = "打开车窗"
    logger.info(f"示例：User: {query}")
    result = send_request(query)
    logger.info(f"示例：Bot: {result}")

    while True:
        try:
            query = input("User: ")
            logger.info(f"User: {query}")
            if query.lower() == 'quit':
                break

            rails_start_time = time.time()
            result = send_request(query)
            rails_cost_time = (time.time() - rails_start_time) * 1000

            user_safety = "none"
            safety_categories = ""
            if result:
                logger.info(f"Bot: {result} (latency={rails_cost_time:.2f}ms)")
                # continue
                try:
                    safety_info = json.loads(result['test_user'])
                    user_safety = safety_info["User Safety"]
                    safety_categories = safety_info["Safety Categories"]
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e}")
                    continue
                except KeyError as e:
                    logger.error(f"Missing required field: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing safety info: {e}")
                    continue
            else:
                logger.error("Error! request failed, please check the connection or logs")
                continue

            wrapper = GPT4OWrapper(API_KEY)
            prompt = generate_response_prompt(
                    query, user_safety, safety_categories
                )
            response, gpt_cost_time = wrapper.chat_completion(
                [{"role": "user", "content": prompt}]
            )
            content = wrapper._process_response(response)
            logger.info(
                f"GPT response: {content} (latency={gpt_cost_time:.2f}ms)"
            )
            logger.info(f"E2E latency: {rails_cost_time + gpt_cost_time:.2f}ms")
        except KeyboardInterrupt:
            logger.info("\nOver!")
            break