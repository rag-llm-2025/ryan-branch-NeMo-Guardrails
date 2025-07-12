# shortcut for nemo guardrails project
# 使用绝对路径更可靠
export NEMO_GUARDRAILS_PRJ_DIR="$HOME/ryan/llm/src/nemo-guardrails"
echo $NEMO_GUARDRAILS_PRJ_DIR

# 添加路径存在性检查
if [ -d "$NEMO_GUARDRAILS_PRJ_DIR" ]; then
    alias nemo-setup-env='cd "$NEMO_GUARDRAILS_PRJ_DIR" && source ./ryan_bot/run_setup_env_ryan_bot.sh'
    alias nemo-server='cd "$NEMO_GUARDRAILS_PRJ_DIR" && source ./ryan_bot/run_server_ryan_bot.sh'
    alias nemo-client='cd "$NEMO_GUARDRAILS_PRJ_DIR" && source ./ryan_bot/run_client_ryan_bot.sh'
else
    echo "警告: NeMo Guardrails项目目录不存在: $NEMO_GUARDRAILS_PRJ_DIR" >&2
fi

# conda别名保持不变
alias nemo-conda-create='conda create -n ryan-guardrails python=3.12 -y'
alias nemo-conda-activate='conda activate ryan-guardrails'
alias nemo-conda-deactivate='conda deactivate'

# cluster server
alias start-cluster='srun --gres=gpu:t4:1 --pty bash -i'
