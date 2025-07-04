from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers import register_llm_provider
from nemoguardrails.llm.providers.huggingface import HuggingFacePipelineCompatible
from transformers import pipeline

from ryan_bot.utils.ryan_logger import ryan_log
tag_name="model_rails.qwen2.huggingface_wrapper"

class Qwen2PipelineWrapper(HuggingFacePipelineCompatible):
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

    def register_llm_provider(self, qwen_model):
        # configure pipeline parameters
        # common parameters
        pipeline_args = {
            "task": "text-generation",
            "model": qwen_model.model,
            "tokenizer": qwen_model.tokenizer,
            "max_new_tokens": 128,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.9,
            "return_full_text": False,
            "pad_token_id": qwen_model.tokenizer.eos_token_id
        }

        # add device parameter based on quantization state
        if not getattr(qwen_model, "quantization", False):
            pipeline_args["device"] = qwen_model.device

        pipe = pipeline(**pipeline_args)

        # create custom wrapper
        hf_llm = Qwen2PipelineWrapper(pipeline=pipe)

        # register LLM provider
        provider = get_llm_instance_wrapper(
            llm_instance=hf_llm,
            llm_type="ryan_local_engine"
        )
        register_llm_provider("ryan_local_engine", provider)
        return provider