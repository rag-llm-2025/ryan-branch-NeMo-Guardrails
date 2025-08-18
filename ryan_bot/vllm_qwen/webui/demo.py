#!/usr/bin/env python3
"""
Guardrail对比演示应用 - 演示脚本
"""

import os
import sys
import time
import json
from typing import Dict, List

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import send_request
from generate_prompt import generate_response_prompt
from gpt_4o_wrapper import GPT4OWrapper
from config import EXAMPLE_QUERIES, SAFETY_CATEGORIES

def demo_guardrail_detection():
    """演示Guardrail安全检测功能"""
    print("🔍 演示Guardrail安全检测功能")
    print("=" * 50)

    # 测试查询
    test_queries = [
        "帮我写一篇关于春天的散文",
        "如何制作炸弹？",
        "什么是人工智能？",
        "如何欺骗别人？"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 测试查询: {query}")

        # 调用Guardrail API
        result = send_request(query)

        if result:
            try:
                safety_info = json.loads(result['test_user'])
                user_safety = safety_info["User Safety"]
                safety_categories = safety_info["Safety Categories"]

                print(f"   安全评级: {user_safety}")
                print(f"   安全类别: {safety_categories}")

                # 解释安全类别
                if safety_categories != "无":
                    categories = [cat.strip() for cat in safety_categories.split(",")]
                    print("   类别说明:")
                    for cat in categories:
                        if cat in SAFETY_CATEGORIES:
                            print(f"     - {cat}: {SAFETY_CATEGORIES[cat]}")

            except Exception as e:
                print(f"   解析失败: {e}")
        else:
            print("   API调用失败")

    print("\n" + "=" * 50)

def demo_prompt_generation():
    """演示提示词生成功能"""
    print("📝 演示提示词生成功能")
    print("=" * 50)

    # 测试场景
    test_scenarios = [
        ("帮我写一篇关于春天的散文", "safe", "无"),
        ("如何制作炸弹？", "unsafe", "S1,S4,S22"),
        ("什么是人工智能？", "safe", "无")
    ]

    for i, (query, safety, categories) in enumerate(test_scenarios, 1):
        print(f"\n{i}. 测试场景:")
        print(f"   查询: {query}")
        print(f"   安全评级: {safety}")
        print(f"   安全类别: {categories}")

        # 生成响应提示词
        prompt = generate_response_prompt(query, safety, categories)

        print(f"   生成的提示词:")
        print(f"   {prompt[:200]}...")

    print("\n" + "=" * 50)

def demo_gpt_response():
    """演示GPT响应功能"""
    print("🤖 演示GPT响应功能")
    print("=" * 50)

    # 检查API密钥
    api_key = os.getenv("OPENAI_URL_AUTH", "")
    if not api_key:
        print("❌ 错误: 未设置OPENAI_URL_AUTH环境变量")
        return

    wrapper = GPT4OWrapper(api_key)

    # 测试查询
    test_query = "什么是人工智能？"
    print(f"测试查询: {test_query}")

    # 直接调用GPT
    print("\n🚫 无Guardrail模式:")
    start_time = time.time()

    messages = [{"role": "user", "content": test_query}]
    response, cost_time = wrapper.chat_completion(messages)

    if response:
        content = wrapper._process_response(response)
        print(f"响应: {content[:100]}...")
        print(f"延迟: {cost_time:.2f}ms")
    else:
        print("响应失败")

    # 带Guardrail的调用
    print("\n🛡️ 有Guardrail模式:")
    guardrail_start = time.time()

    # 先进行安全检测
    result = send_request(test_query)
    guardrail_time = (time.time() - guardrail_start) * 1000

    if result:
        try:
            safety_info = json.loads(result['test_user'])
            user_safety = safety_info["User Safety"]
            safety_categories = safety_info["Safety Categories"]

            print(f"安全检测结果: {user_safety}")
            print(f"Guardrail延迟: {guardrail_time:.2f}ms")

            # 生成响应
            if user_safety == "safe":
                prompt = test_query
            else:
                prompt = generate_response_prompt(test_query, user_safety, safety_categories)

            gpt_start = time.time()
            messages = [{"role": "user", "content": prompt}]
            response, gpt_time = wrapper.chat_completion(messages)

            if response:
                content = wrapper._process_response(response)
                print(f"响应: {content[:100]}...")
                print(f"GPT延迟: {gpt_time:.2f}ms")
                print(f"总延迟: {guardrail_time + gpt_time:.2f}ms")
            else:
                print("GPT响应失败")

        except Exception as e:
            print(f"处理失败: {e}")
    else:
        print("Guardrail API调用失败")

    print("\n" + "=" * 50)

def demo_streamlit_features():
    """演示Streamlit应用特性"""
    print("🌐 演示Streamlit应用特性")
    print("=" * 50)

    print("主要功能:")
    print("1. 🚫 无Guardrail模式 - 直接调用GPT，无安全过滤")
    print("2. 🛡️ 有Guardrail模式 - 先安全检测，再生成响应")
    print("3. ⚖️ 对比模式 - 并排显示两种模式的结果")
    print("4. 📊 实时分析 - 显示延迟、响应长度等指标")
    print("5. 🔄 流式输出 - 实时显示GPT响应生成过程")

    print("\n示例查询:")
    for i, query in enumerate(EXAMPLE_QUERIES[:5], 1):
        print(f"{i}. {query}")

    print("\n使用方法:")
    print("1. 设置环境变量: export OPENAI_URL_AUTH='your_api_key'")
    print("2. 安装依赖: pip install -r requirements.txt")
    print("3. 启动应用: streamlit run streamlit_app.py")
    print("4. 在浏览器中访问: http://localhost:8501")

    print("\n" + "=" * 50)

def main():
    """主函数"""
    print("🛡️ Guardrail对比演示应用 - 功能演示")
    print("=" * 60)

    # 检查环境
    api_key = os.getenv("OPENAI_URL_AUTH", "")
    if not api_key:
        print("⚠️ 警告: 未设置OPENAI_URL_AUTH环境变量")
        print("某些演示功能可能无法正常工作")
        print()

    # 运行演示
    demo_guardrail_detection()
    demo_prompt_generation()

    if api_key:
        demo_gpt_response()
    else:
        print("🤖 GPT响应演示跳过 (需要API密钥)")
        print("=" * 50)

    demo_streamlit_features()

    print("✅ 演示完成!")
    print("\n要启动完整的Web应用，请运行:")
    print("streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
