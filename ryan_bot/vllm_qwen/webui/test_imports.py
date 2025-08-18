#!/usr/bin/env python3
"""
简单的导入测试脚本
"""

def test_imports():
    """测试所有模块导入"""
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
    
    try:
        import streamlit as st
        print("✅ Streamlit 导入成功")
    except ImportError as e:
        print(f"❌ Streamlit 导入失败: {e}")
        print("请安装Streamlit: pip install streamlit")
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

def main():
    """主函数"""
    print("🛡️ Guardrail对比演示应用 - 导入测试")
    print("=" * 60)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败")
        return
    
    # 测试提示词生成
    if not test_prompt_generation():
        print("\n❌ 提示词生成测试失败")
        return
    
    print("\n✅ 所有测试通过！")
    print("\n🚀 启动应用:")
    print("python start_app.py")
    print("或")
    print("streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
