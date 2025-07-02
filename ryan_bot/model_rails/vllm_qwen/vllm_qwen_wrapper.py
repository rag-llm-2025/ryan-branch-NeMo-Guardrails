from nemoguardrails.llm.providers import register_llm_provider
from vllm import LLM, SamplingParams
from nemoguardrails.llm.providers.providers import (
    _acall,
    _chat_providers,
    _get_chat_completion_provider,
    _get_text_completion_provider,
    _llm_providers,
    _parse_version,
    _patch_acall_method_to,
    get_community_chat_provider_names,
    get_llm_provider_names,
    register_chat_provider,
    register_llm_provider,
)


from ryan_bot.utils.ryan_logger import ryan_log
tag_name="model_rails.vllm_qwen.vllm_qwen_wrapper"

class VllmQwenWrapper:
    """自定义适配器，将vLLM集成到Nemo Guardrails"""

    def __init__(self, vllm_model):
        self.model = vllm_model

    async def generate(self, prompt, max_tokens=512, temperature=0.7, top_p=0.9):
        """生成响应的主方法"""
        # 配置采样参数
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            presence_penalty=0.1,  # 减少重复
            frequency_penalty=0.1  # 减少重复
        )

        # 使用vLLM生成响应
        result = self.model.generate(prompt, sampling_params)

        # 提取生成的文本
        generated_text = result[0].outputs[0].text

        return generated_text

    def register_llm_provider(self):
        # configure pipeline parameters

        provider = register_llm_provider("ryan_vllm_engine", self.model)
        # _patch_acall_method_to(provider, _acall)
        ryan_log.info(tag_name, f"get_llm_provider_names: {get_llm_provider_names()}")
        return provider