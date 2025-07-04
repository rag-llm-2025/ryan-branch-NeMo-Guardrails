

from nemoguardrails import RailsConfig

from ryan_bot.model_rails.qwen2.qwen_model import QwenModel
from ryan_bot.model_rails.qwen2.huggingface_wrapper import Qwen2PipelineWrapper

from ryan_bot.utils.helper import print_prompt_loading
from ryan_bot.utils.ryan_logger import ryan_log
tag_name="model_rails.qwen2.helper.py"

def initialize_rails(config: RailsConfig):
    print_prompt_loading(config)

    model_config = next((model for model in config.models if model.type == "main"), None)
    if model_config:
        model_name = model_config.model
        model_path = model_config.parameters.get("model_path")
        checkpoint_path = model_config.parameters.get("checkpoint_path")
        device = model_config.parameters.get("device", "cuda")
        num_gpus = model_config.parameters.get("num_gpus", 1)
        quantization = model_config.parameters.get("quantization", False)
        ryan_log.info(tag_name, f"In config.yml: model_name={model_name}, model_path={model_path}, device={device}, quantization={quantization} checkpoint_path={checkpoint_path}")

        # initialize qwen_model
        qwen_model = QwenModel(model_name, model_path, checkpoint_path=checkpoint_path, device=device, quantization=quantization)
        qwen_model.chat("你对美国最近的暴动怎么看？")

        huggingface_wrapper = Qwen2PipelineWrapper()
        provider = huggingface_wrapper.register_llm_provider(qwen_model)
        ryan_log.debug(tag_name, f"LLM Provider registered: {provider}")