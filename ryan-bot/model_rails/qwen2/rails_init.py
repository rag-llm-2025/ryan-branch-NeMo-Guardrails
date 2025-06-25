
from transformers import pipeline
from nemoguardrails import RailsConfig
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers import register_llm_provider
from nemoguardrails.llm.providers.huggingface import HuggingFacePipelineCompatible

from model_rails.qwen2.qwen_model import QwenModel

class Qwen2PipelineWrapper(HuggingFacePipelineCompatible):
    def __call__(self, prompt: str, **kwargs) -> str:
        print("==============================")
        print("[RYAN_DEBUG] Qwen2PipelineWrapper is called with prompt:", prompt)
        print("[RYAN_DEBUG] Qwen2PipelineWrapper is called with kwargs:", kwargs)
        print("==============================")

        try:
            result = super().__call__(prompt, **kwargs)

            # 处理不同格式的返回结果
            if isinstance(result, list):
                output = result[0].get("generated_text", "")
            else:
                output = result.get("generated_text", "")

            # 确保返回有效内容
            if not output.strip():
                return "[RYAN_DEBUG] I don't have an answer for that."

            return output

        except Exception as e:
            print(f"[RYAN_DEBUG]Error generating response: {str(e)}")
            return "[RYAN_DEBUG] Sorry, I encountered an error while processing your request."

def initialize_rails(config: RailsConfig):
    model_config = next((model for model in config.models if model.type == "main"), None)
    if model_config:
        model_name = model_config.model
        model_path = model_config.parameters.get("model_path")
        checkpoint_path = model_config.parameters.get("checkpoint_path")
        device = model_config.parameters.get("device", "cuda")
        num_gpus = model_config.parameters.get("num_gpus", 1)
        print(f"[RYAN_DEBUG] In config.yml: model_name={model_name}, model_path={model_path}, device={device}, checkpoint_path={checkpoint_path}")

        # 初始化Qwen模型
        qwen_model = QwenModel(model_path, checkpoint_path=checkpoint_path, device=device)
        # print("==================MODEL TEST======================")
        # messages = [
        #             {"role": "system", "content": "你是我的私人助理"},
        #             {"role": "user", "content": "对于美国最近的暴动，你有什么看法？"}
        #         ]
        # print("ryan test input: ", messages[1]["content"])
        # test_response = qwen_model.generate(messages)
        # print("ryan test_response: ", test_response)
        # print("==================MODEL TEST EDN===================\n")


        # 配置pipeline参数
        pipe = pipeline(
            "text-generation",
            model=qwen_model.model,
            tokenizer=qwen_model.tokenizer,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=True,
            return_full_text=False,
            pad_token_id=qwen_model.tokenizer.eos_token_id,
            # repetition_penalty=1.2,  # 添加重复惩罚
            # no_repeat_ngram_size=3   # 防止3-gram重复
        )

        # 使用自定义wrapper封装
        hf_llm = Qwen2PipelineWrapper(pipeline=pipe)

        # 注册LLM provider
        provider = get_llm_instance_wrapper(
            llm_instance=hf_llm,
            llm_type="ryan_local_engine"
        )
        register_llm_provider("ryan_local_engine", provider)
        print(f"[RYAN_DEBUG] LLM Provider registered: {provider}")