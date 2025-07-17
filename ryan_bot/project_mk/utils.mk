# utils.mk - 工具类命令

.PHONY: check_cuda_and_run export_history

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
