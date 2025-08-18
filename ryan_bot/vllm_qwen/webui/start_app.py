#!/usr/bin/env python3
"""
简化的Guardrail对比演示应用启动脚本
"""

import os
import sys
import subprocess

def main():
    """主函数"""
    print("🛡️ Guardrail对比演示应用")
    print("=" * 50)
    
    # 设置默认API密钥（如果环境变量未设置）
    if not os.getenv("OPENAI_URL_AUTH"):
        print("⚠️ 未设置OPENAI_URL_AUTH环境变量，将使用默认API密钥")
    
    print("🚀 启动Streamlit应用...")
    print("🌐 应用将在 http://localhost:8501 启动")
    print("按 Ctrl+C 停止应用\n")
    
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
        print("请确保已安装streamlit: pip install streamlit")

if __name__ == "__main__":
    main()
