import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import os

from transformers import BitsAndBytesConfig

from ryan_bot.utils.ryan_logger import ryan_log
tag_name="model_rails.qwen2.qwen_model.py"

class QwenModel:
    def __init__(self, model_name, model_path, checkpoint_path=None, device="cuda", quantization=False):
        """Initialize Qwen2 local model"""

        ryan_log.info(tag_name, f"Initialize Qwen2 local model, model_path: {model_path}, checkpoint_path: {checkpoint_path}, device: {device}")
        self.model_path = model_path
        self.checkpoint_path = checkpoint_path
        self.device = device
        self.model_name = model_name
        self.quantization = quantization

        ryan_log.info(tag_name, "Loading model and tokenizer...")
        self.tokenizer, self.model = self.load_model(self.model_path, self.checkpoint_path, self.device)
        ryan_log.info(tag_name, "Model and tokenizer loaded successfully.")

    def load_model(self, model_path, checkpoint_path, device):
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        if self.quantization == True:
        # 新增量化配置
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,  # 启用8bit量化
                bnb_8bit_use_double_quant=True,  # 嵌套量化节省更多内存
                bnb_8bit_quant_type="nf8",  # 量化类型
                bnb_8bit_compute_dtype=torch.bfloat16  # 计算精度
            )

            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=quantization_config,
                torch_dtype=torch.bfloat16,  # 保持计算精度
                device_map="auto"          # 自动分配设备
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)

        # only when checkpoint_path is not empty and valid, load peft model
        ryan_log.info(tag_name, f"checkpont_path: {checkpoint_path}")
        if checkpoint_path and os.path.exists(checkpoint_path):
            model = PeftModel.from_pretrained(model, model_id=checkpoint_path)
        else:
            ryan_log.warning(tag_name, f"未提供有效checkpoint_path，仅加载基础模型: {model_path}")

        # Remove manual device assignment for quantized models
        if not getattr(model, "is_loaded_in_8bit", False) or self.quantization == False:
            model = model.to(device)

        model = model.eval()
        return tokenizer, model


    def generate(self, messages, **kwargs):
        """generate reply"""
        if self.model_name == "Qwen2_BE_0.6B":
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
            # ryan_log.info(tag_name, f"Decoded response: {response}")
            return response
        else:
            ryan_log.info(tag_name, f"Not Qwen2_BE_0.6B model, no need to format messages")

            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        # generate response
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=1024)
            ryan_log.info(tag_name, f"Generated outputs: {outputs}")
            response = self.tokenizer.decode(outputs[:, inputs['input_ids'].shape[1]:][0], skip_special_tokens=True)
        # ryan_log.info(tag_name, f"Decoded response: {response}")
        return response

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

    def chat(self, prompt):
        ryan_log.info(tag_name, f"You: {prompt}")
        messages = [
            {"role": "system", "content": "你是我的私人助理"},
            {"role": "user", "content": prompt}
        ]
        response = self.generate(messages)
        ryan_log.info(tag_name, f"Bot: {response}")


        # ryan_test: model test
        # ryan_log.debug(tag_name, "==================MODEL TEST======================")
        # messages = [
        #             {"role": "system", "content": "你是我的私人助理"},
        #             {"role": "user", "content": "对于美国最近的暴动，你有什么看法？"}
        #         ]
        # ryan_log.info(tag_name, "ryan test input: ", messages[1]["content"])
        # test_response = qwen_model.generate(messages)
        # ryan_log.info(tag_name, "ryan test_response: ", test_response)
        # ryan_log.debug(tag_name, "==================MODEL TEST END===================")
