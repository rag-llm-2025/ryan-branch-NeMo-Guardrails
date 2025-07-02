from nemoguardrails.llm.providers import register_llm_provider, get_llm_provider_names
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers.huggingface import HuggingFacePipelineCompatible

from transformers import pipeline

from ryan_bot.model_rails.vllm_qwen.vllm_model_manager import VllmModelManager

from ryan_bot.utils.ryan_logger import ryan_log
tag_name = "model_rails.vllm_qwen.vllm_qwen_wrapper"

from typing import Optional, List

class VllmQwenWrapper(HuggingFacePipelineCompatible):
    vllm_model_manager: Optional[VllmModelManager] = None

    def __init__(self, vllm_model_manager: VllmModelManager):  # 添加构造函数
        super().__init__()
        self.vllm_model_manager = vllm_model_manager

    def __call__(self, prompt: str, **kwargs) -> str:
        ryan_log.info(tag_name, "==============================")
        ryan_log.info(tag_name, "[RYAN_DEBUG] Qwen2PipelineWrapper is called with prompt:", prompt)
        ryan_log.info(tag_name, "[RYAN_DEBUG] Qwen2PipelineWrapper is called with kwargs:", kwargs)
        ryan_log.info(tag_name, "============================")

        try:
            result = super().__call__(prompt, **kwargs)

            # 调试日志
            with open("llm_debug.log", "a") as f:

                f.write(f"[{tag_name}] Prompt: {prompt}\n")
                f.write(f"[{tag_name}] Response: {result}\n\n")

            # 处理不同格式的返回结果
            if isinstance(result, list):
                output = result[0].get("generated_text", "")
            else:
                output = result.get("generated_text", "")

            # 确保返回有效内容
            if not output.strip():
                return f"[{tag_name}] I don't have an answer for that."

            return output

        except Exception as e:
            ryan_log.error(tag_name, f"Error generating response: {str(e)}")
            return f"[{tag_name}] Sorry, I encountered an error while processing your request."

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,  # 添加必须的stop参数
        run_manager = None,  # 添加回调管理器参数
        **kwargs
    ) -> str:
        """实现符合Langchain规范的异步调用接口"""
        ryan_log.info(tag_name, f"异步调用接口，prompt: {prompt[:100]}...")
        try:
            # 将stop参数转换为vLLM需要的格式
            stop_token_ids = []
            if stop:
                stop_token_ids = [self.vllm_model_manager.tokenizer.encode(s, add_special_tokens=False)[-1] for s in stop]

            # 添加stop参数到生成配置
            response = await self.vllm_model_manager.generate_async(
                [prompt],
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
                max_tokens=kwargs.get("max_tokens", 128),
                stop_token_ids=stop_token_ids  # 传递停止token
            )
            ryan_log.info(tag_name, f"异步生成结果response: {response}")
            return response[0]  # 直接返回文本内容

        except Exception as e:
            ryan_log.error(tag_name, f"异步生成错误: {str(e)}")
            return f"[{tag_name}] 异步请求处理失败"

def custom_register_llm_provider(vllm_model_manager):
    # configure pipeline parameters

    # 创建自定义包装器时传递vLLM实例
    hf_llm = VllmQwenWrapper(vllm_model_manager)

    # register LLM provider
    provider = get_llm_instance_wrapper(
        llm_instance=hf_llm,
        llm_type="ryan_vllm_engine"
    )
    register_llm_provider("ryan_vllm_engine", provider)
    ryan_log.info(tag_name, f"可用LLM提供者: {get_llm_provider_names()}")
    return provider