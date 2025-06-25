import argparse
from ruamel.yaml import YAML
from pathlib import Path
import torch
import os

def yml_config_update(config_path, model_name, model_path, device, checkpoint_path):
    """更新config.yml文件中的模型配置，保持原有格式和结构"""
    yaml = YAML()
    yaml.preserve_quotes = True  # 保留字符串的引号
    yaml.indent(mapping=2, sequence=4, offset=2)  # 保持原有缩进

    config_file = Path(config_path) / "config.yml"

    # 读取并保留原有格式
    with open(config_file, 'r') as f:
        config = yaml.load(f)

    # 更新模型配置
    for model in config['models']:
        if model['type'] == 'main':
            model['model'] = model_name
            model['parameters']['model_path'] = model_path
            model['parameters']['device'] = device
            model['parameters']['checkpoint_path'] = checkpoint_path
            print(f"[DEBUG] In config.yml: model_name={model_name}, model_path={model_path}, device={device}, checkpoint_path={checkpoint_path}")

    # 写回文件，保持原有格式
    with open(config_file, 'w') as f:
        yaml.dump(config, f)