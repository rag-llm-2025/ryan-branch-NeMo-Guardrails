# 主Makefile - 核心结构和include语句
# Description:
# cmd: cd nemo-guardrails && make help


# 基础变量定义
LOG_DIR = logs
DATESTR = $(shell date +%Y%m%d-%H%M)

USER = $(shell whoami)
ENV_FILE = ryan_bot/env_setup/.env.$(USER)
HOSTNAME = $(shell hostname)

# load environemnt variables from .env.ryan_niu，such as HOST, PORT, LLM_DIR, MODEL_NAME, MODEL_PATH, DEVICE, CHECKPOINT_PATH
include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))

# 包含子Makefile
include ryan_bot/project_mk/help_project.mk
include ryan_bot/project_mk/env_setup.mk
include ryan_bot/project_mk/server_client.mk
include ryan_bot/project_mk/conda.mk
include ryan_bot/project_mk/utils.mk
include ryan_bot/project_mk/show_allocate_available_gpu.mk

# 默认目标
.PHONY: help
help: help_project
	@echo '----'
	@echo 'test                         - run unit tests'
	@echo 'tests                        - run unit tests'
	@echo 'test TEST_FILE=<test_file>   - run all tests in given file'
	@echo 'test_watch                   - run unit tests in watch mode'
	@echo 'test_coverage                - run unit tests with coverage'
	@echo 'docs                         - build docs, if you installed the docs dependencies'
	@echo 'pre_commit                   - run pre-commit hooks'


.PHONY: all test tests test_watch test_coverage test_profile docs pre_commit help

# Default target executed when no specific target is provided to make.
all: help

# Define a variable for the test file path.
TEST_FILE ?= tests/

test:
	poetry run pytest $(TEST_FILE)

tests:
	poetry run pytest $(TEST_FILE)

test_watch:
	poetry run ptw --snapshot-update --now . -- -vv $(TEST_FILE)

test_coverage:
	poetry run pytest --cov=$(TEST_FILE) --cov-report=term-missing

test_profile:
	poetry run pytest -vv tests/ --profile-svg

docs:
	poetry run sphinx-build -b html docs _build/docs

pre_commit:
	pre-commit install
	pre-commit run --all-files


# HELP

# help:
# 	@echo '----'
# 	@echo 'test                         - run unit tests'
# 	@echo 'tests                        - run unit tests'
# 	@echo 'test TEST_FILE=<test_file>   - run all tests in given file'
# 	@echo 'test_watch                   - run unit tests in watch mode'
# 	@echo 'test_coverage                - run unit tests with coverage'
# 	@echo 'docs                         - build docs, if you installed the docs dependencies'
# 	@echo 'pre_commit                   - run pre-commit hooks'
