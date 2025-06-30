from typing import List, Dict
import requests

from ryan_bot.utils.ryan_logger import ryan_log
tag_name="ryan_bot_client"

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
    def __init__(self, base_url="http://localhost:8000", config_id="qwen_model"):  # set default config_id
        self.base_url = base_url
        self.config_id = config_id

    def chat(self, message: str) -> str:
        payload = {
            "config_id": self.config_id,
            "messages": [{"role": "user", "content": message}]
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
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
    client = RyanBotClient()
    # print("对话开始(输入'quit'退出)")
    ryan_log.info(tag_name, "对话开始(输入'quit'退出)")

    while True:
        user_input = input("You: ")
        ryan_log.info(tag_name, f"User: {user_input}")
        if user_input.lower() == 'quit':
            break

        reply = client.chat(user_input)
        ryan_log.info(tag_name, f"Bot: {reply}")
        # print("AI:", reply)

if __name__ == "__main__":
    interactive_demo()