# env_setup.mk - 环境设置相关命令

.PHONY: setup_env_from_scratch update_env_host print_structure

setup_env_from_scratch: print_structure install_dependencies update_env_host check_cuda_and_run update_yaml_config check_env
	@echo "Done! 完成运行环境部署"

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