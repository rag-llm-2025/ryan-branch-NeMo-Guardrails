import yaml  # 使用PyYAML替代ruamel.yaml
from pathlib import Path

# from nemoguardrails.ryan_logger import ryan_log
# tag_name="utils.helper.py"


def yml_config_update(config_path, engine_name, model_name, model_path, device, checkpoint_path):
    """update config.yml file with model configuration"""
    config_file = Path(config_path)
    if not config_file.is_absolute():
        config_file = Path(__file__).parent.parent / config_path

    print(f"[DEBUG] update yml config: {config_file}")

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at: {config_file}")

    # 读取YAML文件
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    for model in config['models']:
        if model['type'] == 'main':
            model['engine'] = engine_name
            model['model'] = model_name
            model['parameters']['model_path'] = model_path
            model['parameters']['device'] = str(device)
            model['parameters']['checkpoint_path'] = checkpoint_path
            print(f"Updated config.yml with engine_name={engine_name}, model_name={model_name}, model_path={model_path}, device={device}, checkpoint_path={checkpoint_path}")

    # 写入YAML文件
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

def print_prompt_loading(config):
    # ryan_log.info(tag_name, "print loaded prompt templates related to ryan_local_engine ...")
    print("print loaded prompt templates related to ryan_local_engine ...")
    # 优化后的调试输出
    if config.prompts:
        matched_prompts = [
            (p.task, p.models)
            for p in config.prompts
            if p.models and 'ryan_local_engine' in [m.lower() for m in p.models]
        ]
        # ryan_log.debug(tag_name, "===== 匹配的提示模板 =====")
        print("===== 匹配的提示模板 =====")
        for i, (task, models) in enumerate(matched_prompts, 1):
            # ryan_log.debug(tag_name, f"{i}. Task: {task} | Models: {models}")
            print(f"{i}. Task: {task} | Models: {models}")
        # ryan_log.debug(tag_name, f"共匹配 {len(matched_prompts)} 个模板")
        print(f"共匹配 {len(matched_prompts)} 个模板")
    else:
        # ryan_log.warn(tag_name, "警告: 未加载任何提示模板")
        print("警告: 未加载任何提示模板")
