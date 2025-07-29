from nemoguardrails import RailsConfig

from ryan_bot.utils.helper import print_prompt_loading
from nemoguardrails.ryan_logger import ryan_log

tag_name = "rails_init.py"

from ryan_bot.env_setup.env_config import EnvConfig


def initialize_rails(config: RailsConfig):
    # print_prompt_loading(config)

    model_config = next(
        (model for model in config.models if model.type == "main"), None
    )
    if model_config:
        engine_name = model_config.engine
        model_name = model_config.model
        model_path = model_config.parameters.get("model_path")
        checkpoint_path = model_config.parameters.get("checkpoint_path")
        device = model_config.parameters.get("device", "cuda")
        num_gpus = model_config.parameters.get("num_gpus", 1)
        ryan_log.info(
            tag_name,
            f"In config.yml: model_name={model_name}, model_path={model_path}, device={device}, checkpoint_path={checkpoint_path}",
        )

        if EnvConfig.ENABLE_VLLM:
            from ryan_bot.model_rails.vllm_qwen.vllm_model_manager import (
                VllmModelManager,
            )
            from ryan_bot.model_rails.vllm_qwen.vllm_model_wrapper import (
                custom_register_llm_provider,
            )

            # initialize vllm_model
            vllm_model_manager = VllmModelManager(
                model_name,
                model_path,
                checkpoint_path=checkpoint_path,
                device=device,
                tensor_parallel_size=num_gpus,
            )
            # vllm_model_manager.chat("你对美国最近的暴动怎么看？")

            provider = custom_register_llm_provider(vllm_model_manager)
            ryan_log.debug(
                tag_name, f"vllm_qwen_wrapper Provider registered: {provider}"
            )

        else:
            ryan_log.error(tag_name, f"Unknown engine_name: {engine_name}")
            raise ValueError(f"Unknown engine_name: {engine_name}")
