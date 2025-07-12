# conda.mk - Conda环境管理命令

.PHONY: conda_install
conda_install:
	@echo "=== 安装Miniconda并配置环境变量 ==="
	@mkdir -p ~/tools-ryan
	@cd ~/tools-ryan && \
	if ! wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh; then \
		echo "下载Miniconda失败"; exit 1; \
	fi && \
	bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3 && \
	echo 'export PATH="$$HOME/miniconda3/bin:$$PATH"' >> ~/.bashrc && \
	export PATH="$$HOME/miniconda3/bin:$$PATH" && \
	if ! conda --version; then \
		echo "Miniconda安装失败"; exit 1; \
	fi

.PHONY: conda_create
conda_create:
	@echo "=== 创建conda虚拟环境 ==="
	cd $(LLM_DIR)/src/nemo-guardrails && \
	conda create -n ryan-guardrails python=3.12
	@echo "makefile不生效!!!"

.PHONY: conda_activate
conda_activate:
	@echo "=== 激活conda环境 ==="
	@echo "请手动执行以下命令："
	@echo "  conda activate ryan-guardrails"
	@echo "或"
	@echo "  nemo-conda-activate "

.PHONY: conda_deactivate
conda_deactivate:
	@echo "=== 退出conda环境 ==="
	@echo "请手动执行以下命令："
	@echo "  conda deactivate"
	@echo "或"
	@echo "  nemo-conda-deactivate "