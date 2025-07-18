from nemoguardrails.llm.providers import register_llm_provider, get_llm_provider_names
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers.huggingface import HuggingFacePipelineCompatible

from transformers import pipeline

from ryan_bot.model_rails.vllm_qwen.vllm_model_manager import VllmModelManager

from nemoguardrails.ryan_logger import ryan_log
tag_name = "model_rails.vllm_qwen.vllm_qwen_wrapper"

from typing import Optional, List

class VllmQwenWrapper(HuggingFacePipelineCompatible):
    vllm_model_manager: Optional[VllmModelManager] = None

    def __init__(self, vllm_model_manager: VllmModelManager):  # Added constructor
        super().__init__()
        self.vllm_model_manager = vllm_model_manager

    def __call__(self, prompt: str, **kwargs) -> str:
        ryan_log.info(tag_name, "==============================")
        ryan_log.info(tag_name, "[RYAN_DEBUG] Qwen2PipelineWrapper is called with prompt:", prompt)
        ryan_log.info(tag_name, "[RYAN_DEBUG] Qwen2PipelineWrapper is called with kwargs:", kwargs)
        ryan_log.info(tag_name, "============================")

        try:
            result = super().__call__(prompt, **kwargs)

            # Debug logging
            with open("llm_debug.log", "a") as f:
                f.write(f"[{tag_name}] Prompt: {prompt}\n")
                f.write(f"[{tag_name}] Response: {result}\n\n")

            # Handle different response formats
            if isinstance(result, list):
                output = result[0].get("generated_text", "")
            else:
                output = result.get("generated_text", "")

            # Ensure valid content is returned
            if not output.strip():
                return f"[{tag_name}] I don't have an answer for that."

            return output

        except Exception as e:
            ryan_log.error(tag_name, f"Error generating response: {str(e)}")
            return f"[{tag_name}] Sorry, I encountered an error while processing your request."

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager = None,
        **kwargs
    ) -> str:
        """Implement asynchronous call interface compliant with Langchain specifications"""
        ryan_log.critical("kpi", f"VllmQwenWrapper _acall is called.")
        ryan_log.debug(tag_name, f"Async call interface, prompt: {prompt[:100]}...")
        try:
            # Convert stop parameters to vLLM required format
            stop_token_ids = []
            if stop:
                stop_token_ids = [self.vllm_model_manager.tokenizer.encode(s, add_special_tokens=False)[-1] for s in stop]
                kwargs["stop"] = stop_token_ids

            # 确保返回字符串类型结果
            response = await self.vllm_model_manager.generate_async(
                [prompt],
                **kwargs,
                stop_token_ids=stop_token_ids
            )

            ryan_log.debug(tag_name, f"Response type: {type(response)}, content: {response}")

            # 添加类型检查和处理逻辑
            if isinstance(response, list):
                return str(response[0]) if response else ""
            elif isinstance(response, (str, int, float)):
                return str(response)
            else:
                raise ValueError(f"Unsupported response type: {type(response)}")

        except Exception as e:
            ryan_log.error(tag_name, f"Async generation error: {str(e)}")
            return f"[{tag_name}] Async request processing failed"

def custom_register_llm_provider(vllm_model_manager):
    """create and register vllm_qwen_wrapper"""

    # Pass vLLM instance when creating custom wrapper
    hf_llm = VllmQwenWrapper(vllm_model_manager)

    # Register LLM provider
    provider = get_llm_instance_wrapper(
        llm_instance=hf_llm,
        llm_type="ryan_vllm_engine"
    )
    register_llm_provider("ryan_vllm_engine", provider)
    ryan_log.info(tag_name, f"Available LLM providers: {get_llm_provider_names()}")
    return provider