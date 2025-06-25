import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


def log(message):
    print(f"[LOG] {message}")

def load_model(model_path, checkpoint_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    model = PeftModel.from_pretrained(model, model_id=checkpoint_path).to("cpu").eval()
    return tokenizer, model

class QwenModel:
    def __init__(self, model_path, checkpoint_path=None, device="cuda"):
        """初始化Qwen2.5-7B-Instruct模型"""
        self.model_path = model_path
        self.checkpoint_path = checkpoint_path
        self.device = device
        
        log("Loading model and tokenizer...")
        tokenizer, model = load_model(self.model_path, self.checkpoint_path)
        self.tokenizer = tokenizer
        self.model = model
        log("Model and tokenizer loaded successfully.")
    
    def generate(self, messages, **kwargs):
        """生成回复"""
        # 处理输入消息为Qwen模型所需的格式
        # 假设messages格式为OpenAI风格
        prompt = self._format_messages(messages)
        
        # 编码输入
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
    
        
        # 生成回复
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=1024)
            log(f"Generated outputs: {outputs}")
            response = self.tokenizer.decode(outputs[:, inputs['input_ids'].shape[1]:][0], skip_special_tokens=True)
        log(f"Decoded response: {response}")
        return response
        
        # 解码输出
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # 提取模型回复部分（去除prompt）
        final_response = self._extract_response(prompt, response)
        
        return {"role": "assistant", "content": final_response}
    
    def _format_messages(self, messages):
        """将OpenAI风格的消息格式转换为Qwen所需的格式"""
        # Qwen的格式示例: <|im_start|>system\n你是一个助手<|im_end|><|im_start|>user\n你好<|im_end|><|im_start|>assistant\n
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
        # 添加当前用户输入的开始标记
        formatted += "<|im_start|>assistant\n"
        return formatted
    
    def _extract_response(self, prompt, full_response):
        """从完整回复中提取模型生成的部分"""
        # 找到prompt的结束位置
        prompt_end = full_response.find(prompt) + len(prompt)
        # 提取模型生成的内容
        generated_content = full_response[prompt_end:].strip()
        # 去除可能的结束标记
        if "<|im_end|>" in generated_content:
            generated_content = generated_content.split("<|im_end|>")[0].strip()
        return generated_content
