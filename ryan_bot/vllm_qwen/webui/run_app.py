#!/usr/bin/env python3
"""
Guardrail对比演示应用启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """检查环境变量设置"""
    print("🔍 检查环境变量...")
    
    # 检查OpenAI API密钥
    api_key = os.getenv("OPENAI_URL_AUTH")
    if not api_key:
        print("❌ 错误: 未设置 OPENAI_URL_AUTH 环境变量")
        print("请设置您的OpenAI API密钥:")
        print("export OPENAI_URL_AUTH='your_api_key_here'")
        return False
    
    print("✅ OPENAI_URL_AUTH 已设置")
    
    # 检查RAILS_HOST
    rails_host = os.getenv("RAILS_HOST", "localhost")
    print(f"✅ RAILS_HOST: {rails_host}")
    
    return True

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        "streamlit",
        "requests", 
        "openai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n请安装缺失的依赖包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_files():
    """检查必要文件"""
    print("🔍 检查必要文件...")
    
    required_files = [
        "streamlit_app.py",
        "api_client.py", 
        "generate_prompt.py",
        "gpt_4o_wrapper.py"
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
            return False
    
    return True

def start_streamlit():
    """启动Streamlit应用"""
    print("🚀 启动Streamlit应用...")
    
    try:
        # 启动Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🛡️ Guardrail对比演示应用")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查文件
    if not check_files():
        sys.exit(1)
    
    print("\n✅ 所有检查通过!")
    print("🌐 应用将在 http://localhost:8501 启动")
    print("按 Ctrl+C 停止应用\n")
    
    # 启动应用
    start_streamlit()

if __name__ == "__main__":
    main()
