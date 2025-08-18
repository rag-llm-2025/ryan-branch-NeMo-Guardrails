#!/usr/bin/env python3
"""
Guardrail对比演示应用 - 快速测试脚本
"""

import os
import sys
import time
import json

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")

    try:
        from api_client import send_request
        print("✅ api_client 导入成功")
    except ImportError as e:
        print(f"❌ api_client 导入失败: {e}")
        return False

    try:
        from generate_prompt import generate_response_prompt, generate_guardrail_prompt
        print("✅ generate_prompt 导入成功")
    except ImportError as e:
        print(f"❌ generate_prompt 导入失败: {e}")
        return False

    try:
        from gpt_4o_wrapper import GPT4OWrapper
        print("✅ gpt_4o_wrapper 导入成功")
    except ImportError as e:
        print(f"❌ gpt_4o_wrapper 导入失败: {e}")
        return False

    try:
        from config import EXAMPLE_QUERIES, SAFETY_CATEGORIES
        print("✅ config 导入成功")
    except ImportError as e:
        print(f"❌ config 导入失败: {e}")
        return False

    return True

def test_prompt_generation():
    """测试提示词生成"""
    print("\n📝 测试提示词生成...")

    try:
        from generate_prompt import generate_response_prompt, generate_guardrail_prompt

        # 测试guardrail提示词生成
        guardrail_prompt = generate_guardrail_prompt("测试查询")
        print(f"✅ Guardrail提示词生成成功 (长度: {len(guardrail_prompt)}字符)")

        # 测试响应提示词生成
        response_prompt = generate_response_prompt("测试查询", "safe", "无")
        print(f"✅ 响应提示词生成成功 (长度: {len(response_prompt)}字符)")

        return True
    except Exception as e:
        print(f"❌ 提示词生成失败: {e}")
        return False

def test_gpt_wrapper():
    """测试GPT包装器"""
    print("\n🤖 测试GPT包装器...")

    try:
        from gpt_4o_wrapper import GPT4OWrapper

        # 获取API密钥
        api_key = os.getenv("OPENAI_URL_AUTH", "xxx")

        # 创建包装器实例
        wrapper = GPT4OWrapper(api_key)
        print("✅ GPT4OWrapper 实例创建成功")

        return True
    except Exception as e:
        print(f"❌ GPT包装器测试失败: {e}")
        return False

def test_config():
    """测试配置文件"""
    print("\n⚙️ 测试配置文件...")

    try:
        from config import EXAMPLE_QUERIES, SAFETY_CATEGORIES, COLORS

        print(f"✅ 示例查询数量: {len(EXAMPLE_QUERIES)}")
        print(f"✅ 安全类别数量: {len(SAFETY_CATEGORIES)}")
        print(f"✅ 颜色配置数量: {len(COLORS)}")

        return True
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False

def test_streamlit_import():
    """测试Streamlit导入"""
    print("\n🌐 测试Streamlit导入...")

    try:
        import streamlit as st
        print("✅ Streamlit 导入成功")
        return True
    except ImportError as e:
        print(f"❌ Streamlit 导入失败: {e}")
        print("请安装Streamlit: pip install streamlit")
        return False

def main():
    """主函数"""
    print("🛡️ Guardrail对比演示应用 - 快速测试")
    print("=" * 60)

    tests = [
        ("模块导入", test_imports),
        ("配置文件", test_config),
        ("提示词生成", test_prompt_generation),
        ("GPT包装器", test_gpt_wrapper),
        ("Streamlit", test_streamlit_import),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 测试失败")

    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("✅ 所有测试通过！应用可以正常运行")
        print("\n🚀 启动应用:")
        print("python start_simple.py")
        print("或")
        print("streamlit run streamlit_app.py")
    else:
        print("❌ 部分测试失败，请检查依赖和环境")
        print("\n💡 建议:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 检查Python环境")
        print("3. 确保所有文件都在同一目录下")

if __name__ == "__main__":
    main()
