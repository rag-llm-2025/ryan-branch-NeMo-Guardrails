from vllm import LLM, SamplingParams
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import torch
import os

from ryan_bot.utils.ryan_logger import ryan_log
tag_name = "model_rails.v_qwen.vllm_qwen_model.py"


class ModelConfig(BaseModel):
    """模型配置参数容器"""
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
        """初始化模型管理器"""
        self.config = ModelConfig(
            model_name=model_name,
            model_path=model_path,
            checkpoint_path=checkpoint_path,
            device=device,
            tensor_parallel_size=tensor_parallel_size
        )
        self._validate_paths()

        # 初始化默认采样参数
        self.default_params = {
            "temperature": 0.7,
            "top_p": 0.8,
            "max_tokens": 512
        }

        ryan_log.info(tag_name,
            f"初始化vLLM模型 | 路径: {self.config.model_path} | "
            f"设备: {self.config.device} | 并行度: {self.config.tensor_parallel_size}"
        )

        self.model = self.load_model()
        self.tokenizer = self.model.get_tokenizer()  # 确保tokenizer可用

    def _validate_paths(self):
        """路径验证逻辑"""
        if not os.path.exists(self.config.model_path):
            raise FileNotFoundError(f"模型路径不存在: {self.config.model_path}")
        if self.config.checkpoint_path and not os.path.exists(self.config.checkpoint_path):
            ryan_log.warning(tag_name, f"Peft模型路径不存在: {self.config.checkpoint_path}")

    def load_model(self) -> LLM:
        """加载vLLM模型引擎"""
        try:
            return LLM(
                model=self.config.model_path,
                tensor_parallel_size=torch.cuda.device_count(),
                dtype=self.config.dtype,
                gpu_memory_utilization=self.config.gpu_memory_utilization,
                trust_remote_code=True
            )
        except Exception as e:
            ryan_log.error(tag_name, f"模型加载失败: {str(e)}")
            raise

    def _get_sampling_params(self, **kwargs) -> SamplingParams:
        """生成采样参数"""
        params = {**self.default_params, **kwargs}
        return SamplingParams(**params)

    def generate(self, prompts: List[str], **kwargs) -> List[str]:
        """同步生成接口"""
        params = self._get_sampling_params(**kwargs)
        outputs = self.model.generate(prompts, params)
        return [self._process_output(o) for o in outputs]

    async def generate_async(self, prompts: List[str], **kwargs) -> List[str]:
        """异步生成接口 (vLLM原生支持)"""

        ryan_log.info(tag_name, f"异步生成请求 | 提示: {prompts} | 参数: {kwargs}")
        params = self._get_sampling_params(**kwargs)
        outputs = self.model.generate(prompts, params)
        return [self._process_output(o) for o in outputs]

    def _process_output(self, output) -> str:
        """统一输出处理"""
        text = output.outputs[0].text
        return text.split("<|im_end|>")[0].strip()

    def chat(self, prompt: str, **kwargs) -> str:
        """对话接口"""
        ryan_log.debug(tag_name, f"处理用户输入: {prompt[:60]}...")

        system_prompt = "你是我的私人助理"
        full_prompt = f"系统: {system_prompt}\n用户: {prompt}\n助手:"

        try:
            response = self.generate([full_prompt], **kwargs)[0]
            ryan_log.debug(tag_name, f"生成响应: {response[:60]}...")
            return response
        except Exception as e:
            ryan_log.error(tag_name, f"对话生成失败 | 错误: {str(e)}")
            return "抱歉，生成响应时出现错误"