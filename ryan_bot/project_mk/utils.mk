# utils.mk - 工具类命令

.PHONY: check_cuda_and_run update_yaml_config install_dependencies print_env check_env export_history

check_cuda_and_run:
	@echo "检查CUDA可用性..."
	@if command -v nvidia-smi &> /dev/null && \
	   command -v nvcc &> /dev/null && \
	   python3 -c "import torch; print(torch.cuda.is_available())" | grep -q 'True'; then \
		echo "CUDA is available. Displaying GPU information:"; \
		nvidia-smi; \
		echo "Setting device to cuda"; \
		export DEVICE="cuda"; \
	else \
		echo "CUDA is not available. Using CPU."; \
		export DEVICE="cpu"; \
	fi

update_yaml_config:
	@echo "更新YAML配置..."
	cd $(LLM_DIR)/src/nemo-guardrails/ryan_bot/ && \
	python3 -c "from utils.helper import yml_config_update; yml_config_update('./config/qwen_model/config.yml', '${ENGINE_NAME}', '${MODEL_NAME}', '${MODEL_PATH}', '${DEVICE}', '${CHECKPOINT_PATH}')"

install_dependencies:
	@echo "安装依赖..."
	cd $(LLM_DIR)/src/nemo-guardrails/ && pip install -e .
	cd $(LLM_DIR)/src/nemo-guardrails/ryan_bot/ && pip install -r requirements.txt

print_env:
	@printf "\033[1;36m=== .env文件导入环境变量 ===\033[0m\n"
	@printf "  \033[1;35mUSER:\033[0m $(USER)\n"
	@printf "  \033[1;35mHOST:\033[0m $(HOST)\n"
	@printf "  \033[1;35mPORT:\033[0m $(PORT)\n"
	@printf "  \033[1;35mLLM_DIR:\033[0m $(LLM_DIR)\n"
	@printf "  \033[1;35mMODEL_NAME:\033[0m $(MODEL_NAME)\n"
	@printf "  \033[1;35mMODEL_PATH:\033[0m $(MODEL_PATH)\n"
	@printf "  \033[1;35mDEVICE:\033[0m $(DEVICE)\n"
	@printf "  \033[1;35mCHECKPOINT_PATH:\033[0m $(CHECKPOINT_PATH)\n"
	@printf "  \033[1;35mAPI_KEY:\033[0m $(API_KEY)\n"
	@printf "  \033[1;35mAPI_SECRET:\033[0m $(API_SECRET)\n"

check_env:
	cd $(LLM_DIR)/src/nemo-guardrails/ryan_bot/ && python3 -c "import nemoguardrails; print(nemoguardrails.__version__)"

export_history:
	@echo "正在导出命令历史记录..."
	@history_file="$(LOG_DIR)/history_$(DATESTR).log"; \
	echo "=== 命令历史记录 ===" > $$history_file; \
	echo "用户: $(USER)" >> $$history_file; \
	echo "主机: $(HOSTNAME)" >> $$history_file; \
	echo "时间: $(shell date)" >> $$history_file; \
	echo "" >> $$history_file; \
	[ -f ~/.bash_history ] && cat ~/.bash_history >> $$history_file || \
	# [ -f ~/.zsh_history ] && cat ~/.zsh_history >> $$history_file || \
	echo "无法获取命令历史记录" >> $$history_file; \
	echo "历史记录已保存到: $$history_file"
