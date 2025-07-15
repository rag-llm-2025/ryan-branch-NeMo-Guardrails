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

# 加载多个安全数据集
datasets = {
    "aegis": load_dataset("nvidia/Aegis-AI-Content-Safety-Dataset-1.0"),
    "toxic": load_dataset("skg/toxic_comments"),
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

    if "comment_text" in examples:  # 有害评论数据集
        for text in examples["comment_text"]:
            inputs.append(f"用户：{text}\n助手：")
            targets.append("这个问题可能包含不当内容，我无法回答。")

    if "prompt" in examples:  # 安全提示数据集
        for prompt, response in zip(examples["prompt"], examples["response"]):
            inputs.append(prompt)
            targets.append(response)

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

# 训练参数配置
training_args = TrainingArguments(
    output_dir="./qwen2.5-safe",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-5,
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=50,
    evaluation_strategy="steps",
    eval_steps=500,
    save_strategy="epoch",
    fp16=True,
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