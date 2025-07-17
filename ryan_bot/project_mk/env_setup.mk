# env_setup.mk - 环境设置相关命令

.PHONY: setup_env_from_scratch update_yaml_config install_dependencies print_env check_env update_env_host print_structure

setup_env_from_scratch: print_structure install_dependencies update_env_host check_cuda_and_run update_yaml_config check_env
	@echo "Done! 完成运行环境部署"

update_yaml_config:
	@echo "更新YAML配置..."
	cd $(LLM_DIR)/src/nemo-guardrails/ryan_bot/ && \
	python3 -c "from utils.helper import yml_config_update; yml_config_update('./config/qwen_model/config.yml', '${ENGINE_NAME}', '${MODEL_NAME}', '${MODEL_PATH}', '${DEVICE}', '${CHECKPOINT_PATH}')"

install_dependencies:
	@echo "安装依赖..."
	cd $(LLM_DIR)/src/nemo-guardrails/ && pip3 install -e .
	cd $(LLM_DIR)/src/nemo-guardrails/ryan_bot/ && pip3 install -r requirements.txt

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
	@printf "\033[1;36m=== 项目配置开关 ===\033[0m\n"
	@printf "  \033[1;35mSTREAM:\033[0m $(STREAM)\n"
	@printf "  \033[1;35mENABLE_VLLM:\033[0m $(ENABLE_VLLM)\n"
	@printf "  \033[1;35mENABLE_TEXT_EMBEDDING:\033[0m $(ENABLE_TEXT_EMBEDDING)\n"
	@printf "  \033[1;35mENABLE_LATENCY_OPTIMIZATION:\033[0m $(ENABLE_LATENCY_OPTIMIZATION)\n"

check_env:
	cd $(LLM_DIR)/src/nemo-guardrails/ryan_bot/ && python3 -c "import nemoguardrails; print(nemoguardrails.__version__)"

update_env_host:
	@echo "machine name: $(USER)@$(HOSTNAME)"
	@echo "env file: $(ENV_FILE)"
	@NEW_HOST=$$(hostname -I | awk '{print $$1}'); \
	if [ -z "$$NEW_HOST" ]; then \
		echo "无法获取主机IP地址"; \
		exit 1; \
	fi; \
	echo "NEW_HOST: $$NEW_HOST"; \
	if [ "$(USER)" = "ryan_niu" ] && [ "$(HOSTNAME)" = "gn403" ]; then \
		echo "当前用户是ryan_niu, 且hostname是gn403时, 替换HOST为: $$NEW_HOST"; \
		sed -i "s/^HOST=.*/HOST=$$NEW_HOST/" "$(ENV_FILE)"; \
		echo "已将$(ENV_FILE)中的HOST更新为: $$NEW_HOST"; \
	fi

print_structure:
	@echo "示例目录结构："
	@echo "/home/ubuntu/llm"
	@echo "├── models"
	@echo "│   ├── Qwen2_BE_0.6B"
	@echo "│   └── deepseek"
	@echo "└── src"
	@echo "    ├── nemo-guardrails"
	@echo "        └── config"
	@echo "            └── qwen_model"
	@echo "                └── config.yml"