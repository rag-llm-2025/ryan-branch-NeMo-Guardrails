from ruamel.yaml import YAML
from pathlib import Path

# from nemoguardrails.ryan_logger import ryan_log
# tag_name="utils.helper.py"

def yml_config_update(config_path, engine_name, model_name, model_path, device, checkpoint_path):
    """update config.yml file with model configuration, keeping the original format and structure"""
    yaml = YAML()
    yaml.preserve_quotes = True  # keep the original quotes
    yaml.indent(mapping=2, sequence=4, offset=2)  # keep the original indentation

    # config_file = Path(config_path) / "config.yml"
    # convert to absolute path
    config_file = Path(config_path)
    if not config_file.is_absolute():
        # if relative path, resolve based on the script directory
        config_file = Path(__file__).parent.parent / config_path

    print(f"[DEBUG] update yml config: {config_file}")

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at: {config_file}")

    # read and keep the original format
    with open(config_file, 'r') as f:
        config = yaml.load(f)

    # update model configuration
    for model in config['models']:
        if model['type'] == 'main':
            model['engine'] = engine_name
            model['model'] = model_name
            model['parameters']['model_path'] = model_path
            model['parameters']['device'] = str(device)
            model['parameters']['checkpoint_path'] = checkpoint_path
            # ryan_log.info(tag_name, f"Updated config.yml with engine_name={engine_name}, model_name={model_name}, model_path={model_path}, device={device}, checkpoint_path={checkpoint_path}")
            print(f"Updated config.yml with engine_name={engine_name}, model_name={model_name}, model_path={model_path}, device={device}, checkpoint_path={checkpoint_path}")

    # write back to file, keeping the original format
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

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
