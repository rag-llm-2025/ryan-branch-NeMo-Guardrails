from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
import os

# 模型和分词器加载
model_name = "Qwen/Qwen2.5-7B-Instruct"
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # 设置pad token

# 加载多个安全数据集 (更新版)
try:
    datasets = {
        "aegis": load_dataset("nvidia/Aegis-AI-Content-Safety-Dataset-1.0"),
        "toxic": load_dataset("allenai/real-toxicity-prompts"),  # 替代数据集
        "harmonization": load_dataset("ethz-spylab/harmonization")
    }
except Exception as e:
    print(f"加载数据集时出错: {str(e)}")
    # 回退到仅使用可用的数据集
    datasets = {
        "aegis": load_dataset("nvidia/Aegis-AI-Content-Safety-Dataset-1.0"),
        "harmonization": load_dataset("ethz-spylab/harmonization")
    }

def prepare_safety_data(examples):
    inputs = []
    targets = []

    # 处理不同数据集的字段
    if "text" in examples:  # Aegis数据集
        for text in examples["text"]:
            inputs.append(f"用户：{text}\n助手：")
            targets.append("抱歉，这个问题我无法回答。")

    if "prompt" in examples and "response" in examples:  # harmonization数据集
        for prompt, response in zip(examples["prompt"], examples["response"]):
            inputs.append(prompt)
            targets.append(response)

    if "text" in examples and "toxicity" in examples:  # real-toxicity-prompts数据集
        for text, toxicity in zip(examples["text"], examples["toxicity"]):
            if toxicity > 0.5:  # 只使用高毒性样本
                inputs.append(f"用户：{text}\n助手：")
                targets.append("这个问题可能包含不当内容，我无法回答。")

    # 统一tokenize处理
    model_inputs = tokenizer(
        inputs,
        truncation=True,
        padding="max_length",
        max_length=512
    )

    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            targets,
            truncation=True,
            padding="max_length",
            max_length=512
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
    per_device_train_batch_size=4,  # 从2提升到4 (V100可承受)
    gradient_accumulation_steps=4,   # 从8降低到4 (与batch_size乘积保持16)
    learning_rate=3e-5,             # 适当提高学习率
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=50,
    evaluation_strategy="steps",
    eval_steps=500,
    save_strategy="epoch",
    fp16=True,                      # V100支持FP16加速
    gradient_checkpointing=True,    # 新增: 启用梯度检查点节省显存
    optim="adamw_torch_fused",      # 新增: 使用融合优化器
    max_grad_norm=1.0,              # 新增: 梯度裁剪
    warmup_ratio=0.1,               # 新增: 学习率预热
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    report_to="tensorboard"
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