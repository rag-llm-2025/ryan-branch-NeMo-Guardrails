.PHONY: project_help
project_help:
	@printf "\033[1;36m\n=== 可用命令 ===\033[0m\n"
	@printf "\033[1;33m环境设置:\033[0m\n"
	@echo "  make setup_env_from_scratch   - 从零开始部署运行环境"
	@echo "  make install_dependencies     - 安装nemo guardrails和ryan_bot环境依赖"
	@echo "  make check_cuda_and_run       - 检查cuda是否可用，设置device"
	@echo "  make update_yaml_config       - 更新YAML配置"
	@echo "  make check_env                - 测试运行环境"
	@echo "  make print_env                - 打印.env文件导入的环境变量"
	@echo "  make update_env_host          - 更新指定服务器的IP地址"
	@echo "  make export_history           - 导出历史记录"
	@echo "  make custom_bashrc_cmd        - 自定义.bashrc命令"

	@printf "\n\033[1;33mGPU资源管理:\033[0m\n"
	@echo "  make allocate_gpu GPU_TYPE=h100 GPU_NUM=1 MEM_GB=100 - 自动申请指定GPU资源"
	@echo "  make check_gpu GPU_TYPE=h100  - 检查GPU资源是否可用"

	@printf "\n\033[1;33m运行命令:\033[0m\n"
	@echo "  make server                   - 启动服务端"
	@echo "  make client                   - 启动客户端"

	@printf "\n\033[1;33mConda命令:\033[0m\n"
	@echo "  make conda_install            - 安装conda环境"
	@echo "  make conda_create             - 创建conda环境"
	@echo "  make conda_activate           - 激活conda环境"
	@echo "  make conda_deactivate         - 停用conda环境"

	@printf "\n\033[1;33m调试命令:\033[0m\n"
	@echo "  make check_cuda               - 检查CUDA可用性"

	@printf "\n\033[1;36m=== 重要环境变量 ===\033[0m\n"
	@printf "  \033[1;35mUSER:\033[0m $(USER)\n"
	@printf "  \033[1;35mHOST:\033[0m $(HOST)\n"
	@printf "  \033[1;35mPORT:\033[0m $(PORT)\n"
	@printf "  \033[1;35mLLM_DIR:\033[0m $(LLM_DIR)\n"
	@printf "  \033[1;35mMODEL_PATH:\033[0m $(MODEL_PATH)\n"
	@printf "  \033[1;35mDEVICE:\033[0m $(DEVICE)\n"
