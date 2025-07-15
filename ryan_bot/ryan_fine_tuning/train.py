from huggingface_hub import login
import os
token = os.getenv(key="HF_TOKEN", default=None)  # 从环境变量中获取Hugging Face的token
print(f" huggingface token: {token}")
login(token=token)

from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)

# Add this before TrainingArguments
try:
    from transformers.integrations import TensorBoardCallback
    report_to = ["tensorboard"]
except ImportError:
    print("TensorBoard not available - falling back to default logging")
    report_to = None


# 模型和分词器加载
model_name = "Qwen/Qwen2.5-7B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    use_cache=False  # 显式禁用缓存以兼容梯度检查点
)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

dataset_directory = "./dataset"

# 加载多个安全数据集 (更新版)
try:
    datasets = {
        "aegis": load_dataset("nvidia/Aegis-AI-Content-Safety-Dataset-1.0", cache_dir=dataset_directory),
        "toxic": load_dataset("allenai/real-toxicity-prompts", cache_dir=dataset_directory),
        "safety": load_dataset("Anthropic/hh-rlhf", cache_dir=dataset_directory)  # 替代harmonization
    }
except Exception as e:
    print(f"加载数据集时出错: {str(e)}")
    # 最小可用数据集
    datasets = {
        "aegis": load_dataset("nvidia/Aegis-AI-Content-Safety-Dataset-1.0"),
        "safety": load_dataset("Dahoas/rm-static")  # 备用数据集
    }

def prepare_safety_data(examples):
    inputs = []
    targets = []

    # 处理不同数据集的字段
    if "text" in examples:  # Aegis数据集
        for text in examples["text"]:
            if isinstance(text, str) and text.strip():  # 确保是字符串且非空
                inputs.append(f"用户：{text}\n助手：")
                targets.append("抱歉，这个问题我无法回答。")

    if "chosen" in examples:  # hh-rlhf数据集
        for text in examples["chosen"]:
            if isinstance(text, str) and "Assistant:" in text and text.strip():
                parts = text.split("Assistant:")
                inputs.append(parts[0].replace("Human:", "用户：") + "助手：")
                targets.append(parts[1].strip())

    if "text" in examples and "toxicity" in examples:  # real-toxicity-prompts数据集
        for text, toxicity in zip(examples["text"], examples["toxicity"]):
            if isinstance(text, str) and text.strip() and toxicity > 0.5:
                inputs.append(f"用户：{text}\n助手：")
                targets.append("这个问题可能包含不当内容，我无法回答。")

    # 如果没有任何有效输入，返回空字典
    if not inputs:
        return {}

    # 统一tokenize处理
    model_inputs = tokenizer(
        inputs,
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    )

    # 使用text_target参数替代as_target_tokenizer
    labels = tokenizer(
        text_target=targets,
        truncation=True,
        padding="max_length",
        max_length=512,
        return_tensors="pt"
    ).input_ids

    model_inputs["labels"] = labels
    return model_inputs

# 预处理所有数据集
processed_datasets = []
for name, dataset in datasets.items():
    processed = dataset.map(
        prepare_safety_data,
        batched=True,
        remove_columns=dataset["train"].column_names
    )
    processed_datasets.append(processed["train"])

# 合并数据集并划分训练/验证集
full_dataset = concatenate_datasets(processed_datasets)
split_dataset = full_dataset.train_test_split(test_size=0.1)
train_dataset = split_dataset["train"]
eval_dataset = split_dataset["test"]

# 数据整理器
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# 训练参数配置 (V100优化版)
training_args = TrainingArguments(
    output_dir="./qwen2.5-safe",
    per_device_train_batch_size=2,  # 从2提升到4 (V100可承受)
    gradient_accumulation_steps=8,   # 从8降低到4 (与batch_size乘积保持16)
    learning_rate=2e-5,             # 适当提高学习率
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=50,
    eval_strategy="epoch",  # Changed to match save_strategy
    save_strategy="epoch",
    fp16=True,                      # V100支持FP16加速
    gradient_checkpointing=True,    # 新增: 启用梯度检查点节省显存
    optim="adamw_torch_fused",      # 新增: 使用融合优化器
    max_grad_norm=1.0,              # 新增: 梯度裁剪
    warmup_ratio=0.1,               # 新增: 学习率预热
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    report_to=report_to  # Modified to handle missing tensorboard
)

# 初始化Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
)

# 开始训练
trainer.train()

# 保存最佳模型
model_save_path = os.path.join(os.path.dirname(__file__), "content_safety_model")
trainer.save_model(model_save_path)
tokenizer.save_pretrained(model_save_path)