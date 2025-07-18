from vllm import LLM, SamplingParams
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import torch
import os

from nemoguardrails.ryan_logger import ryan_log
tag_name = "model_rails.v_qwen.vllm_qwen_model.py"
from ryan_bot.env_setup.env_config import EnvConfig


class ModelConfig(BaseModel):
    """Model configuration parameter container"""
    model_name: str
    model_path: str
    checkpoint_path: Optional[str] = None
    device: str = "cuda"
    tensor_parallel_size: int = 1
    dtype: str = "bfloat16"
    gpu_memory_utilization: float = 0.9


class VllmModelManager:
    def __init__(self, model_name: str, model_path: str, checkpoint_path: Optional[str] = None,
                 device: str = "cuda", tensor_parallel_size: int = 1):
        """Initialize model manager"""
        self.config = ModelConfig(
            model_name=model_name,
            model_path=model_path,
            checkpoint_path=checkpoint_path,
            device=device,
            tensor_parallel_size=tensor_parallel_size
        )
        self._validate_paths()

        # Initialize default sampling parameters
        self.default_params = {
            "max_tokens": 40,  # 增加到32768
            "temperature": 0.7,
            "top_p": 0.8,
            "min_p": 0.1,  # 新增参数，提高生成质量
            "skip_special_tokens": True  # 跳过特殊token
        }

        ryan_log.info(tag_name,
            f"Initializing vLLM model | Path: {self.config.model_path} | "
            f"设备: {self.config.device} | 并行度: {self.config.tensor_parallel_size}"
        )

        self.model = self.load_model()
        self.tokenizer = self.model.get_tokenizer()  # Ensure tokenizer is available

    def _validate_paths(self):
        """Path validation logic"""
        if not os.path.exists(self.config.model_path):
            raise FileNotFoundError(f"Model path does not exist: {self.config.model_path}")
        if self.config.checkpoint_path and not os.path.exists(self.config.checkpoint_path):
            ryan_log.warning(tag_name, f"Peft model path does not exist: {self.config.checkpoint_path}")

    def load_model(self) -> LLM:
        """Load vLLM model engine"""
        try:
            return LLM(
                model=self.config.model_path,
                tensor_parallel_size=torch.cuda.device_count(),
                dtype=self.config.dtype,
                gpu_memory_utilization=self.config.gpu_memory_utilization,
                trust_remote_code=True
            )
        except Exception as e:
            ryan_log.error(tag_name, f"Model loading failed: {str(e)}")
            raise

    def _get_sampling_params(self, **kwargs) -> SamplingParams:
        """Generate sampling parameters with enhanced validation"""
        # 合并默认参数和传入参数
        params = {**self.default_params, **kwargs}

        # 确保参数类型正确
        for key in ["temperature", "top_p", "min_p"]:
            if key in params and not isinstance(params[key], (int, float)):
                ryan_log.warning(tag_name, f"Invalid type for {key}, converting to float")
                params[key] = float(params[key])

        # 确保stop_token_ids是列表类型
        if "stop_token_ids" in params and not isinstance(params["stop_token_ids"], list):
            params["stop_token_ids"] = [params["stop_token_ids"]]

        return SamplingParams(**params)

    def generate(self, prompts: List[str], **kwargs) -> List[str]:
        """Synchronous generation interface"""
        ryan_log.info(tag_name, f"for generation method, call generate_async instead")
        self.generate_async(prompts, **kwargs)

    async def generate_async(self, prompts: List[str], **kwargs) -> List[str]:
        """Asynchronous generation interface with enhanced error handling"""
        ryan_log.debug(tag_name, f"Async generation request | Prompts: {prompts}")

        try:
            # 获取并验证采样参数
            # params = self._get_sampling_params(**kwargs)
            params=SamplingParams(self.default_params)
            ryan_log.info(tag_name, f"Sampling params: {params}")

            # 调用模型生成
            outputs = await self.model.generate(prompts, params)

            # 验证返回结果
            if not isinstance(outputs, list):
                raise TypeError(f"Expected list output, got {type(outputs)}")

            return [self._process_output(o) for o in outputs]

        except Exception as e:
            ryan_log.error(tag_name, f"Generation failed: {str(e)}")
            return ["[Error] Failed to generate response"] * len(prompts)

    def _process_output(self, output) -> str:
        """Unified output processing"""
        text = output.outputs[0].text
        ryan_log.debug(tag_name, f"raw text: \n{text}")
        return text.split("<|im_end|>")[0].strip()

    def chat(self, prompt: str, **kwargs) -> str:
        """Chat interface"""
        ryan_log.debug(tag_name, f"Processing user input: {prompt[:60]}...")

        system_prompt = "You are my personal assistant"
        full_prompt = f"System: {system_prompt}\nUser: {prompt}\nAssistant:"

        try:
            response = self.generate([full_prompt], **kwargs)[0]
            # ryan_log.debug(tag_name, f"Bot: {response[:60]}...")
            ryan_log.debug(tag_name, f"Bot: {response}")
            return response
        except Exception as e:
            ryan_log.error(tag_name, f"Chat generation failed | Error: {str(e)}")
            return "Sorry, an error occurred while generating the response"