from typing import Optional, Generator
import requests
import time
import os
import json
from requests.exceptions import RequestException

from simple_logger import RyanLogger as logger
from nemoguardrails.ryan_logger import ryan_log

from gpt_4o_verify import GPT4OWrapper
from generate_prompt import generate_response_prompt, generate_guardrail_prompt

# api_server address and port
RAILS_HOST = os.getenv("RAILS_HOST", "localhost")
logger.info(f"RAILS_HOST: {RAILS_HOST}")
API_KEY = os.getenv("OPENAI_URL_AUTH", "")

API_URL = f"http://{RAILS_HOST}:8010/generate"
HEADERS = {"Content-Type": "application/json"}
MAX_RETRIES = 3
ENABLE_QWEN_GUARDRAIL = True

def send_request(query: str) -> Optional[dict]:
    """send_request to server"""
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

async def print_response(content: str, cost_time: float):
    for char in content:
        print(char, end='', flush=True)
        time.sleep(0.02)
    logger.info(f"\n(latency={cost_time:.2f}ms)")

if __name__ == "__main__":
    wrapper = GPT4OWrapper(API_KEY)
    query = "帮我写一篇关于春天的散文，字数在1000字左右"
    logger.info(f"示例：User: {query}")
    result = send_request(query)
    logger.info(f"示例：Bot: {result}")

    while True:
        try:
            query = input("User: ")
            logger.info(f"User: {query}")
            if query.lower() == 'quit':
                break

            # send request to gpt server
            rails_start_time = time.time()
            result = send_request(query)
            qwen_guardrail_latency = (time.time() - rails_start_time) * 1000

            if not result:
                logger.error("Error! request failed")
                continue

            try:
                safety_info = json.loads(result['test_user'])
                user_safety = safety_info["User Safety"]
                safety_categories = safety_info["Safety Categories"]
            except Exception as e:
                logger.error(f"Error processing safety info: {e}")
                continue

            if ENABLE_QWEN_GUARDRAIL:
                prompt = generate_response_prompt(query, user_safety, safety_categories)
            else:
                prompt = query

            # streaming output
            logger.info("Bot: ")
            first_chunk = True
            first_chunk_time = None
            gpt_guardrail_time = None
            response = []

            gpt_start_time = time.time()
            ryan_log.info("Start streaming output")
            for chunk in wrapper.stream_chat_completion([{"role": "user", "content": prompt}]):
                if isinstance(chunk, dict):
                    gpt_guardrail_time = time.time()
                    ryan_log.info(f"gpt_guardrail_result: {chunk}")
                    continue
                else:
                    response.append(chunk)

                if first_chunk:
                    first_chunk_time = time.time()
                    first_chunk = False
                ryan_log.info(f"chunk: {chunk}")

            completion_output = ''.join(response)
            logger.info(f"Bot: {completion_output}")
            final_chunk_time = time.time()

            logger.info("Latency Measurement:")
            logger.critical(f"Qwen Guardrails latency: {qwen_guardrail_latency:.2f}ms")

            if gpt_guardrail_time:
                gpt_guardrail_latency = (gpt_guardrail_time - gpt_start_time) * 1000
                logger.critical(f"GPT Guardrails latency: {gpt_guardrail_latency:.2f}ms")

            if first_chunk_time:
                first_response_latency = (first_chunk_time - gpt_start_time) * 1000
                logger.critical(f"First response latency: {first_response_latency:.2f}ms")

            gpt_e2e_latency = (final_chunk_time - gpt_start_time) * 1000
            logger.critical(f"GPT response latency: {gpt_e2e_latency:.2f}ms")

            logger.critical(f"E2E latency: {qwen_guardrail_latency + gpt_e2e_latency:.2f}ms")

        except KeyboardInterrupt:
            logger.info("\nOver!")
            break