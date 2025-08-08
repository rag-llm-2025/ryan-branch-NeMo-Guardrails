import logging
from typing import Optional
import requests
import time
import os
from requests.exceptions import RequestException
from nemoguardrails.logging.verbose import console

from simple_logger import RyanLogger as logger

# api_server address and port
RAILS_HOST = os.getenv("RAILS_HOST", "localhost")
print("RAILS_HOST:", RAILS_HOST)

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

            result = send_request(query)
            if result:
                logger.info(f"Bot: {result}")
            else:
                logger.error("Error! request failed, please check the connection or logs")
        except KeyboardInterrupt:
            logger.info("\nOver!")
            break