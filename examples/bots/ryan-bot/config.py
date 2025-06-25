import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers import register_llm_provider
from nemoguardrails.llm.providers.huggingface import HuggingFacePipelineCompatible

import sys
sys.path.append("./")
from qwen_model import QwenModel


def init_main_llm(config: RailsConfig):
    model_config = next((model for model in config.models if model.type == "main"), None)
    if model_config:
        model_path = model_config.parameters.get("path")
        device = model_config.parameters.get("device", "cuda")
        num_gpus = model_config.parameters.get("num_gpus", 1)

        # 模型本地路径
        # model_path = "/home/ubuntu/workspace/llm/ryan-qwen2-fine-tuning/model/wen2_BE_0.6B"
        checkpoint_path="/home/ubuntu/workspace/llm/ryan-qwen2-fine-tuning/qwen2/output/hotel_qwen2-ryan-test-20250611/checkpoint-1000"

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

        pipe = pipeline(
            "text-generation",
            model=qwen_model.model,
            tokenizer=qwen_model.tokenizer,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=True,
        )

        hf_llm = HuggingFacePipelineCompatible(pipeline=pipe)
        provider = get_llm_instance_wrapper(
            llm_instance=hf_llm, llm_type="ryan_local_engine"
        )
        register_llm_provider("ryan_local_engine", provider)

def init(llm_rails: LLMRails):
    config = llm_rails.config
    init_main_llm(config)
