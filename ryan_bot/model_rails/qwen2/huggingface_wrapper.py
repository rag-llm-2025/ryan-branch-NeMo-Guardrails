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

    def register_llm_provider(self, qwen_model):
        # Configure pipeline parameters
        pipe = pipeline(
            "text-generation",
            model=qwen_model.model,
            tokenizer=qwen_model.tokenizer,
            device=qwen_model.device,
            max_new_tokens=128,
            temperature=0.7,  # Can be adjusted dynamically as needed
            do_sample=True,
            # top_k=50,
            top_p=0.9,
            return_full_text=False,
            pad_token_id=qwen_model.tokenizer.eos_token_id,
            # repetition_penalty=1.2,  # add repetition penalty
            # no_repeat_ngram_size=3   # prevent 3-gram repetition
        )

        ryan_log.info(tag_name, pipe.model.generation_config.num_return_sequences)
        test = "你对美国的印象是什么？"
        output = pipe(test, max_new_tokens=10)
        if isinstance(output, list):
            logged_output = output[0].get("generated_text", "")
        else:
            logged_output = output.get("generated_text", "")
        ryan_log.info(tag_name, test + " --> " +logged_output)

        # Create custom wrapper
        hf_llm = Qwen2PipelineWrapper(pipeline=pipe)

        # Register LLM provider
        provider = get_llm_instance_wrapper(
            llm_instance=hf_llm,
            llm_type="ryan_local_engine"
        )
        register_llm_provider("ryan_local_engine", provider)
        return provider