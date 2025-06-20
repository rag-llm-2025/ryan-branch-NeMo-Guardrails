import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers import register_llm_provider
from nemoguardrails.llm.providers.huggingface import HuggingFacePipelineCompatible

def _load_model(model_name_or_path, device, num_gpus, debug=False):
    if device == "cpu":
        kwargs = {}
    elif device == "cuda":
        kwargs = {"torch_dtype": torch.float16}
        if num_gpus == "auto":
            kwargs["device_map"] = "auto"
        else:
            num_gpus = int(num_gpus)
            if num_gpus != 1:
                kwargs.update(
                    {
                        "device_map": "auto",
                        "max_memory": {i: "13GiB" for i in range(num_gpus)},
                    }
                )
    elif device == "mps":
        kwargs = {"torch_dtype": torch.float16}
        print("mps not supported")
    else:
        raise ValueError(f"Invalid device: {device}")

    # 检查是否为本地路径, 添加 local_files_only=True 参数
    if os.path.isdir(model_name_or_path):
        model_name_or_path = os.path.abspath(model_name_or_path)
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=False, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path, low_cpu_mem_usage=True, **kwargs, local_files_only=True
        )
    else:
        # 如果不是本地路径，按原逻辑处理
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=False)
        model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path, low_cpu_mem_usage=True, **kwargs
        )

    if device == "cuda" and num_gpus == 1:
        model.to(device)

    if debug:
        print(model)

    return model, tokenizer

def init_main_llm(config: RailsConfig):
    model_config = next((model for model in config.models if model.type == "main"), None)
    if model_config:
        model_path = model_config.parameters.get("path")
        device = model_config.parameters.get("device", "cuda")
        num_gpus = model_config.parameters.get("num_gpus", 1)

        model, tokenizer = _load_model(
            model_path, device, num_gpus, debug=False
        )

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=True,
        )

        hf_llm = HuggingFacePipelineCompatible(pipeline=pipe)
        provider = get_llm_instance_wrapper(
            llm_instance=hf_llm, llm_type="hf_pipeline_local"
        )
        register_llm_provider("hf_pipeline_local", provider)

def init(llm_rails: LLMRails):
    config = llm_rails.config
    init_main_llm(config)
