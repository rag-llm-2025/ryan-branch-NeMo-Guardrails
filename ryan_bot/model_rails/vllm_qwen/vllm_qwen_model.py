from vllm import LLM, SamplingParams
from langchain_core.language_models.llms import BaseLLM
from typing import List, Dict, Any, Optional
import asyncio
import json

import torch
import os

from ryan_bot.utils.ryan_logger import ryan_log
tag_name="model_rails.vllm_qwen.vllm_qwen_model.py"

class VllmQwenModel(BaseLLM):
    def __init__(self, model_name, model_path, checkpoint_path=None, device="cuda"):
        """Initialize Qwen2 local model"""

        ryan_log.info(tag_name, f"Initialize Qwen2 local model, model_path: {model_path}, checkpoint_path: {checkpoint_path}, device: {device}")
        self.model_path = model_path
        self.checkpoint_path = checkpoint_path
        self.device = device
        self.model_name = model_name

        ryan_log.info(tag_name, "Loading model and tokenizer...")
        self.model = self.load_model(self.model_path, self.checkpoint_path, self.device)
        ryan_log.info(tag_name, "Model and tokenizer loaded successfully.")

    def load_model(self, model_path, checkpoint_path, device):
        """创建vLLM推理引擎并加载本地模型
        Args:
            model_path: 基础模型路径
            checkpoint_path: Peft模型路径
            device: 运行设备
        """
        # 保留原有checkpoint加载逻辑
        if checkpoint_path and os.path.exists(checkpoint_path):
            ryan_log.warning(tag_name, "vLLM暂不支持直接加载Peft模型，请使用merge后的模型")

        # vLLM初始化配置
        llm = LLM(
            model=model_path,
            tensor_parallel_size=torch.cuda.device_count(),
            dtype="bfloat16",
            gpu_memory_utilization=0.9,
            trust_remote_code=True  # 允许加载远程代码
        )
        return llm

    def generate(self, messages):
        """生成模型回复
        Args:
            messages: 对话消息列表
        """
        # 转换messages为vLLM输入格式
        vllm_inputs = [
            {
                "prompt": message["content"],
                "parameters": SamplingParams(
                    temperature=0.7,
                    top_p=0.9,
                    max_tokens=128,
                ),
            }
            for message in messages
        ]

        # 调用vLLM生成回复
        results = self.model.generate(vllm_inputs)

        # 提取回复文本
        responses = [result.outputs[0].text for result in results]

        return responses

    def _call(self, *args, **kwargs):
        return "Mock response"

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager = None,
        **kwargs,
    ) -> str:
        ryan_log.info(tag_name, f"_acall prompt: {prompt}")
        """更新后的异步调用方法，兼容LangChain接口"""

        ryan_log.info(tag_name, "==============================")
        ryan_log.info(tag_name, "[vLLM_DEBUG] vLLMWrapper _acall() called with prompt:", prompt)
        ryan_log.info(tag_name, "[vLLM_DEBUG] vLLMWrapper _acall() called with kwargs:", kwargs)
        ryan_log.info(tag_name, "============================")

        try:
            # 合并stop参数到采样参数
            current_params = self.sampling_params
            if stop:
                current_params = SamplingParams(
                    temperature=kwargs.get('temperature', current_params.temperature),
                    top_p=kwargs.get('top_p', current_params.top_p),
                    max_tokens=kwargs.get('max_tokens', current_params.max_tokens),
                    stop=stop  # 使用传入的stop tokens
                )

            outputs = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.llm.generate([prompt], current_params)
            )
            response_text = outputs[0].outputs[0].text
            return json.dumps({"generated_text": response_text})
        except Exception as e:
            ryan_log.error(tag_name, f"vLLM async generation error: {str(e)}")
            raise ValueError(f"[ERROR] {str(e)}")



    def _generate(self, *args, **kwargs):
        ryan_log.info(tag_name, "Mock generate called")
        self.generate(args, kwargs)
        return "Mock generation"

    def _llm_type(self):
        return "ryan_mock_llm_type"

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
