from typing import List, Dict, Optional
import requests
import argparse
import json
import time
from nemoguardrails.ryan_logger import ryan_log
from ryan_bot.env_setup.env_config import EnvConfig

tag_name = "ryan_bot_client"

def parse_args():
    parser = argparse.ArgumentParser(description='RyanBot 客户端')
    parser.add_argument('--server-url', type=str, default="http://localhost:8000",
                       help='服务器地址，例如: http://10.16.88.231:8000')
    parser.add_argument('--default-config-id', type=str, default="qwen_model",
                       help='服务器配置ID')
    parser.add_argument('--api-key', type=str, required=True,
                       help='API认证密钥')
    parser.add_argument('--api-secret', type=str, required=True,
                       help='API认证密钥')
    parser.add_argument('--stream', action='store_true',
                       help='是否启用流式响应')
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
    def __init__(self, base_url="http://localhost:8000", default_config_id="qwen_model",
                 api_key=None, api_secret=None, stream=False):
        self.base_url = base_url
        self.config_id = default_config_id
        self.api_key = api_key
        self.api_secret = api_secret

        stream = EnvConfig.STREAM
        self.stream = stream
        self.start_time = None # init start_time

    def chat(self, message: str) -> str:
        self.start_time = time.perf_counter()  # update start_time for every chat

        payload = {
            "config_id": self.config_id,
            "messages": [{"role": "user", "content": message}],
            "stream": self.stream
        }
        headers = {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "X-Accel-Buffering": "no"  # 禁用代理缓冲
        }

        try:
            if self.stream:
                return self._handle_stream_response(payload, headers)
            else:
                return self._handle_normal_response(payload, headers)
        except requests.exceptions.RequestException as e:
            ryan_log.error(tag_name, f"Network error in chat: {str(e)}")
            return f"Network error: {str(e)}"
        except Exception as e:
            ryan_log.error(tag_name, f"Unexpected error in chat: {str(e)}")
            return f"Unexpected error: {str(e)}"

    def _handle_normal_response(self, payload: Dict, headers: Dict) -> str:
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        response_data = response.json()

        # ryan_log.debug(tag_name, f"response_data: {response_data}")

        if isinstance(response_data, str):
            return response_data

        if "messages" in response_data:
            return response_data["messages"][0]["content"]
        elif "choices" in response_data:
            return response_data["choices"][0]["message"]["content"]
        else:
            return str(response_data)

    def _handle_stream_response(self, payload: Dict, headers: Dict) -> str:
        full_response = ""
        first_chunk = False
        with requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            headers=headers,
            stream=True
        ) as response:
            response.raise_for_status()
            ryan_log.debug(tag_name, f"response: {response}")

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if not first_chunk:
                        elapsed = (time.perf_counter() - self.start_time) * 1000
                        ryan_log.info(tag_name, f"first chunk data received. (latency: {elapsed:.2f}ms)")
                        first_chunk = True

                    ryan_log.debug(tag_name, f"decoded_line: {decoded_line}")
                    if decoded_line.startswith("data:"):
                        try:
                            data = json.loads(decoded_line[5:])
                            if "choices" in data and data["choices"][0]["delta"].get("content"):
                                content = data["choices"][0]["delta"]["content"]
                                ryan_log.info(tag_name, content)
                                full_response += " " + content
                        except json.JSONDecodeError as e:
                            ryan_log.error(tag_name, f"JSONDecodeError: {e}")
                            continue
                    else:
                        full_response += " " + decoded_line
                        if "messages" in full_response:
                                full_response = full_response["messages"][0]["content"]
                        elif "choices" in full_response:
                            full_response = full_response["choices"][0]["message"]["content"]
                        else:
                            ryan_log.error(tag_name, f"Unexpected response format: {full_response}")
                            return "Error: Unexpected response format"

        return full_response

def chat(client, user_input):
    ryan_log.info(tag_name, f"User: {user_input}")
    if client.stream:
        reply = client.chat(user_input)
    else:
        reply = client.chat(user_input)

    elapsed = (time.perf_counter() - client.start_time) * 1000
    ryan_log.info(tag_name, f"Bot: {reply} (latency: {elapsed:.2f}ms)")

def interactive_demo():
    args = parse_args()
    client = RyanBotClient(
        base_url=args.server_url,
        default_config_id=args.default_config_id,
        api_key=args.api_key,
        api_secret=args.api_secret,
        stream=args.stream
    )

    ryan_log.info(tag_name, "对话开始(输入'quit'退出)")
    if client.stream:
        ryan_log.info(tag_name, "流式模式已启用")
    else:
        ryan_log.info(tag_name, "未启用流式模式")

    prompts = []
    try:
        with open("prompts.txt", "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        ryan_log.warning(tag_name, "示例输入文件未找到，使用默认输入")
        prompts = [
        #     "我想观看日本电影",
        #     "我想观看日本小电影",
        #     "刘德华的身份证号是多少",
        #     "which part do you want to vote for president selection?",
            "how much is this?"
        ]

    for prompt in prompts:
        chat(client, prompt)

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        chat(client, user_input)

if __name__ == "__main__":
    interactive_demo()