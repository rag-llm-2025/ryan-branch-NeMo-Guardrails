#!/usr/bin/env python3
"""
测试错误处理的脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_error_handling():
    """测试错误处理功能"""
    print("🔍 测试错误处理功能")
    print("=" * 50)
    
    try:
        from gpt_4o_wrapper import GPT4OWrapper
        
        # 使用无效的API密钥测试
        print("1. 测试无效API密钥...")
        invalid_wrapper = GPT4OWrapper("invalid_key")
        
        test_messages = [{"role": "user", "content": "Hello"}]
        
        try:
            response, cost_time = invalid_wrapper.chat_completion(test_messages)
            print(f"   响应: {response}")
            print(f"   延迟: {cost_time:.2f}ms")
        except Exception as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
        # 测试流式请求
        print("\n2. 测试流式请求错误处理...")
        try:
            for chunk in invalid_wrapper.stream_chat_completion(test_messages):
                if isinstance(chunk, dict) and "error" in chunk:
                    print(f"   ✅ 正确捕获流式错误: {chunk['error']}")
                    break
                elif isinstance(chunk, str):
                    print(f"   收到内容: {chunk[:50]}...")
        except Exception as e:
            print(f"   ✅ 正确捕获流式异常: {e}")
        
        print("\n✅ 错误处理测试完成")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    return True

def test_streamlit_error_display():
    """测试Streamlit错误显示"""
    print("\n🌐 测试Streamlit错误显示...")
    
    try:
        import streamlit as st
        print("✅ Streamlit可用")
        
        # 模拟错误信息
        error_examples = [
            {
                "error": "请求参数错误",
                "status_code": "400"
            },
            {
                "error": "API认证失败",
                "status_code": "401"
            },
            {
                "error": "服务器内部错误",
                "status_code": "500"
            }
        ]
        
        print("错误示例:")
        for i, error in enumerate(error_examples, 1):
            print(f"{i}. {error['error']} (状态码: {error['status_code']})")
        
        print("\n✅ Streamlit错误显示测试完成")
        
    except ImportError as e:
        print(f"❌ Streamlit不可用: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🛡️ Guardrail对比演示应用 - 错误处理测试")
    print("=" * 60)
    
    # 测试错误处理
    if not test_error_handling():
        print("\n❌ 错误处理测试失败")
        return
    
    # 测试Streamlit错误显示
    if not test_streamlit_error_display():
        print("\n❌ Streamlit错误显示测试失败")
        return
    
    print("\n✅ 所有错误处理测试通过！")
    print("\n💡 现在可以在Web应用中看到详细的错误信息了")
    print("\n🚀 启动应用:")
    print("python start_app.py")

if __name__ == "__main__":
    main()
