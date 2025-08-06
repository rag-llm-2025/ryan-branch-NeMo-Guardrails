from datasets import load_dataset, load_from_disk
import os
import json


def load_and_process_aegis_dataset():
    """加载并处理 Aegis 内容安全数据集"""
    try:
        cache_path = "../hf_model_cache/datasets"
        if os.path.exists(cache_path):
            dataset = load_from_disk(cache_path)
        else:
            dataset = load_dataset(
                "nvidia/Aegis-AI-Content-Safety-Dataset-1.0",
                split="train",
                trust_remote_code=True,
            )
            dataset.save_to_disk(cache_path)

        # 打印数据集信息
        print("\n数据集结构:")
        print(dataset)

        print("\n前3条数据demo:")
        for i in range(3):
            print(f"数据 {i+1}: {dataset[i]}")

        return dataset

    except Exception as e:
        print(f"加载数据集时出错: {e}")
        return None


def export_filtered_corpus(dataset, output_dir="./output/filtered_corpus"):
    """根据条件过滤语料并以JSON格式输出"""
    try:
        os.makedirs(output_dir, exist_ok=True)

        output_files = {
            "user_message": open(
                f"{output_dir}/user_messages.jsonl", "w", encoding="utf-8"
            ),
            "llm_response": open(
                f"{output_dir}/llm_responses.jsonl", "w", encoding="utf-8"
            ),
        }

        for example in dataset:
            text = example.get("text", "")
            text_type = example.get("text_type", "")
            label = example.get("labels_2", "")
            if label is None:
                label = example.get("labels_0", "")

            if label is None:
                continue

            if isinstance(label, str) and label.lower() == "safe":
                continue

            if text_type in output_files and text:
                record = {"text": text, "text_type": text_type, "label": label}
                output_files[text_type].write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

        for file in output_files.values():
            file.close()

        print(f"\n生成路径： {output_dir}")
        print(f"生成文件: {', '.join(output_files.keys())}")

    except Exception as e:
        print(f"导出语料时出错: {e}")


if __name__ == "__main__":
    aegis_dataset = load_and_process_aegis_dataset()

    if aegis_dataset is not None:
        export_filtered_corpus(aegis_dataset)
