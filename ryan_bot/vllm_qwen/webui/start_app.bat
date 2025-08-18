@echo off
chcp 65001 >nul
echo 🛡️ Guardrail对比演示应用
echo ================================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查环境变量
if "%OPENAI_URL_AUTH%"=="" (
    echo ❌ 错误: 未设置OPENAI_URL_AUTH环境变量
    echo 请设置您的OpenAI API密钥:
    echo set OPENAI_URL_AUTH=your_api_key_here
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo 🚀 启动应用...

REM 启动应用
python run_app.py

pause
