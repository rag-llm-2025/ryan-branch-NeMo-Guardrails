import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os

from ryan_bot.utils.ryan_logger import ryan_log
tag_name="model_rails.qwen2.qwen_model.py"


def load_model(model_path, checkpoint_path, device):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    ryan_log.info(tag_name, f"checkpont_path: {checkpoint_path}")

    # only when checkpoint_path is not empty and valid, load peft model
    if checkpoint_path and os.path.exists(checkpoint_path):
        model = PeftModel.from_pretrained(model, model_id=checkpoint_path)
    else:
        ryan_log.warning(tag_name, f"未提供有效checkpoint_path，仅加载基础模型: {model_path}")

    model = model.to(device).eval()
    return tokenizer, model

class QwenModel:
    def __init__(self, model_path, checkpoint_path=None, device="cuda"):
        """Initialize Qwen2 local model"""

        ryan_log.info(tag_name, f"Initialize Qwen2 local model, model_path: {model_path}, checkpoint_path: {checkpoint_path}, device: {device}")
        self.model_path = model_path
        self.checkpoint_path = checkpoint_path
        self.device = device

        ryan_log.info(tag_name, "Loading model and tokenizer...")
        tokenizer, model = load_model(self.model_path, self.checkpoint_path, self.device)
        self.tokenizer = tokenizer
        self.model = model
        ryan_log.info(tag_name, "Model and tokenizer loaded successfully.")


    def generate(self, messages, **kwargs):
        """generate reply"""

        # handling input messages to the format required by Qwen model
        # images format is assumed to be OpenAI style
        ryan_log.info(tag_name, f"Input messages: {messages}")
        prompt = self._format_messages(messages)
        ryan_log.info(tag_name, f"Formatted prompt: {prompt}")

        # tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # generate response
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=1024)
            ryan_log.info(tag_name, f"Generated outputs: {outputs}")
            response = self.tokenizer.decode(outputs[:, inputs['input_ids'].shape[1]:][0], skip_special_tokens=True)
        ryan_log.info(tag_name, f"Decoded response: {response}")
        return response

        # decode the output tokens to text
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # extract the model response part (remove prompt)
        final_response = self._extract_response(prompt, response)

        return {"role": "assistant", "content": final_response}

    def _format_messages(self, messages):
        """convert OpenAI messages to Qwen format"""

        # Qwen message format: <|im_start|>system\n你是一个助手<|im_end|><|im_start|>user\n你好<|im_end|><|im_start|>assistant\n
        formatted = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                formatted += f"<|im_start|>system\n{content}<|im_end|>"
            elif role == "user":
                formatted += f"<|im_start|>user\n{content}<|im_end|>"
            elif role == "assistant":
                formatted += f"<|im_start|>assistant\n{content}<|im_end|>"

        # add current user input start tag
        formatted += "<|im_start|>assistant\n"
        return formatted

    def _extract_response(self, prompt, full_response):
        """extract response from full response"""

        # find prompt end
        prompt_end = full_response.find(prompt) + len(prompt)

        # extract generated content
        generated_content = full_response[prompt_end:].strip()

        # remove the end tag if exists
        if "<|im_end|>" in generated_content:
            generated_content = generated_content.split("<|im_end|>")[0].strip()

        return generated_content
