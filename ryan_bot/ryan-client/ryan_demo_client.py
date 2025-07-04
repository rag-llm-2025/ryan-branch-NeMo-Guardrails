from typing import List, Dict
import requests
import argparse

from ryan_bot.utils.ryan_logger import ryan_log
tag_name="ryan_bot_client"


# 新增参数解析函数
def parse_args():
    parser = argparse.ArgumentParser(description='RyanBot 客户端')
    parser.add_argument('--server-url', type=str, default="http://localhost:8000",
                        help='服务器地址，例如: http://10.16.88.231:8000')
    parser.add_argument('--config-id', type=str, default="qwen_model",
                        help='服务器配置ID')
    parser.add_argument('--api-key', type=str, required=True,
                        help='API认证密钥')
    parser.add_argument('--api-secret', type=str, required=True,
                        help='API认证密钥')
    return parser.parse_args()

""" response json format
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      }
    }
  ]
}
"""
class RyanBotClient:
    def __init__(self, base_url="http://localhost:8000", config_id="qwen_model", api_key=None, api_secret=None):
        self.base_url = base_url
        self.config_id = config_id
        self.api_key = api_key
        self.api_secret = api_secret

    def chat(self, message: str) -> str:
        payload = {
            "config_id": self.config_id,
            "messages": [{"role": "user", "content": message}]
        }
        headers = {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
                # timeout=10
            )
            response.raise_for_status()

            # check response format
            response_data = response.json()
            if isinstance(response_data, str):
                return response_data

            if "messages" in response_data:
                return response_data["messages"][0]["content"]
            elif "choices" in response_data:
                return response_data["choices"][0]["message"]["content"]
            else:
                return str(response_data)

        except Exception as e:
            return f"Error: {str(e)}"

def interactive_demo():
    args = parse_args()
    client = RyanBotClient(
        base_url=args.server_url,
        config_id=args.config_id,
        api_key=args.api_key,
        api_secret=args.api_secret
    )
    # print("对话开始(输入'quit'退出)")
    ryan_log.info(tag_name, "对话开始(输入'quit'退出)")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        import time
        start_time = time.perf_counter()
        ryan_log.info(tag_name, f"User: {user_input}")
        reply = client.chat(user_input)
        elapsed = (time.perf_counter() - start_time) * 1000  # 毫秒
        ryan_log.info(tag_name, f"Bot: {reply} (latency: {elapsed:.2f}ms]")

if __name__ == "__main__":
    interactive_demo()