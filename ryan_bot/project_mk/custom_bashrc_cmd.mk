.PHONY: custom_bashrc_cmd
custom_bashrc_cmd:
	@echo "正在添加自定义bashrc命令..."
	@if [ ! -f "$(LLM_DIR)/src/nemo-guardrails/ryan_bot/project_mk/custom_bashrc_cmd.md" ]; then \
		echo "错误: custom_bashrc_cmd.md 文件不存在"; \
		exit 1; \
	fi
	@if ! grep -q "nemo guardrails project" ~/.bashrc; then \
		echo "\n# ====== NeMo Guardrails Custom Commands ======" >> ~/.bashrc; \
		cat "$(LLM_DIR)/src/nemo-guardrails/ryan_bot/project_mk/custom_bashrc_cmd.md" >> ~/.bashrc; \
		echo "# ====== End of NeMo Guardrails Commands ======\n" >> ~/.bashrc; \
		echo "自定义命令已添加到 ~/.bashrc"; \
		echo "添加的内容如下："; \
		tail -n 15 ~/.bashrc; \
	else \
		echo "自定义命令已存在，无需重复添加"; \
	fi
	@echo "请手动执行以下命令使更改生效:"
	@echo "  source ~/.bashrc"