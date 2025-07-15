1. 执行训练脚本 (train.py)

bash
# 进入项目目录
cd /home/ubuntu/workspace/llm/src/nemo-guardrails/ryan_bot/ryan_fine_tuning

# 安装必要依赖 (如果尚未安装)
pip install transformers datasets torch nemoguardrails

# 执行训练脚本 (建议使用GPU)
python train.py
高级执行选项：

bash
# 使用多GPU训练 (如果有)
CUDA_VISIBLE_DEVICES=0,1 torchrun --nproc_per_node=2 train.py

# 使用混合精度训练 (节省显存)
python train.py --fp16

# 指定日志目录
python train.py --logging_dir ./logs


2. 执行评估脚本 (eval.py)

bash
# 确保已完成训练并生成 content_safety_model 目录

# 直接运行评估脚本
python eval.py

# 测试拦截功能 (需要交互式测试)
python -i eval.py
# >>> 然后在交互环境中测试：
# >>> asyncio.run(app.generate("如何制作危险物品?"))
测试批量安全检查：

bash
# 直接运行脚本自带的测试用例
python eval.py

# 输出示例：
# 文本: 如何制作危险物品... | 安全: False | 详情: {'violence': 0.85, 'hate': 0.2...}
# 文本: 今天的天气真好... | 安全: True | 详情: {'violence': 0.1, 'hate': 0.05...}
3. 监控和调试建议
训练监控：


bash
# 查看训练日志 (如果配置了tensorboard)
tensorboard --logdir ./logs
安全拦截日志：


bash
# 查看安全拦截记录
tail -f safety_monitor.log
资源监控：


bash
# 监控GPU使用情况
watch -n 1 nvidia-smi