import streamlit as st
import time
import json
from typing import Optional, Dict, List, Tuple, Any
import os
import traceback

# 模块导入
from api_client import send_request
from generate_prompt import generate_response_prompt
from gpt_4o_wrapper import GPT4OWrapper
from config import (
    APP_TITLE,
    APP_ICON,
    EXAMPLE_QUERIES,
    COLORS,
    get_latency_color,
    format_safety_categories
)

# 类型定义
ProcessResult = Dict[str, Any]
SafetyInfo = Dict[str, Optional[str]]

# 初始化页面配置
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_gpt_wrapper() -> GPT4OWrapper:
    """初始化并缓存GPT包装器"""
    return GPT4OWrapper(os.getenv("OPENAI_URL_AUTH"))

class UIComponents:
    """可复用的UI组件工厂"""
    @staticmethod
    def create_progress_container(container) -> Tuple[Any, Any]:
        """创建进度条容器"""
        progress_bar = container.progress(0)
        status_text = container.empty()
        return progress_bar, status_text

    @staticmethod
    def create_mode_buttons():
        """创建模式选择按钮"""
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🚀 GPT原生生成模式")

            # 模式说明
            # - 🚫 风险内容基本拦截
            # st.markdown("""
            # - ⚡ 直接调用GPT大模型
            # - 💨 400异常外抛安全信息
            # """)

            # 操作按钮
            direct_btn = st.button(
                "🚀 立即生成",
                key="direct_btn",
                use_container_width=True,
                type="primary",
                help="直接调用GPT模型，不经过安全过滤"
            )

        with col2:
            st.subheader("🛡️ Guardrail安全检测模式")

            # 模式说明
            # - ⚠️ 风险内容分类
            # st.markdown("""
            # - 🔍 内容安全检测
            # - 📊 安全报告生成
            # """)

            # 操作按钮
            guardrail_btn =  st.button(
                "🛡️ 安全生成",
                key="guardrail_btn",
                use_container_width=True,
                type="secondary",
                help="先进行安全检测再生成响应"
            )

        return direct_btn, guardrail_btn

    @staticmethod
    def show_header():
        """显示应用页眉"""
        st.title("🛡️ Guardrails功能对比演示")
        st.markdown("**版本:** 1.2.0 | **最后更新:** 2025-08-15")
        st.markdown("---")

    @staticmethod
    def show_footer():
        """显示应用页脚"""
        st.markdown("---")
        st.caption("© 2025 Cerence AI Research | [隐私政策](/#) | [服务条款](/#)")

class SafetyHandler:
    """安全检测处理模块"""
    @staticmethod
    def format_safety_info(safety_info: SafetyInfo) -> str:
        """格式化安全检测结果"""
        if not safety_info:
            return "无安全信息"

        user_safety = safety_info.get("User Safety", "unknown")
        safety_color = COLORS["unsafe"] if user_safety == "unsafe" else COLORS["safe"]
        categories = format_safety_categories(safety_info.get("Safety Categories"))

        return f"""
        {safety_color} **Guardrail安全评级**: {user_safety}
        **检测类别**: {categories}
        """

    @staticmethod
    def format_callm_info(safety_info: SafetyInfo) -> str:
        """格式化安全检测结果"""
        if not safety_info:
            return "无安全信息"

        user_safety = safety_info.get("User Safety", "unknown")
        safety_color = COLORS["unsafe"] if user_safety == "unsafe" else COLORS["safe"]
        categories = format_safety_categories(safety_info.get("Safety Categories"))

        return f"""
        {safety_color} **CaLLM安全评级**: {user_safety}
        **检测类别**: {categories}
        """

    @classmethod
    def check_safety(cls, user_input: str) -> Tuple[Optional[SafetyInfo], Optional[float]]:
        """执行安全检测"""
        start_time = time.time()
        result = send_request(user_input)

        if not result:
            return None, None

        try:
            safety_info = json.loads(result['test_user'])
            if 'User Safety' not in safety_info:
                raise ValueError("响应缺少必要字段'User Safety'")
            latency = (time.time() - start_time) * 1000
            return safety_info, latency
        except Exception as e:
            st.error(f"🔍 安全检测响应解析失败: {str(e)}\n原始响应: {result}")
            return None, None

class ResponseHandler:
    """响应处理基类"""
    @staticmethod
    def stream_response(wrapper: GPT4OWrapper, messages: List[Dict], placeholder_key: str) -> Optional[str]:
        """流式输出响应"""
        if placeholder_key not in st.session_state:
            st.session_state[placeholder_key] = st.empty()

        placeholder = st.session_state[placeholder_key]

        response_text = ""
        error_occurred = False
        error_message = ""

        try:
            for chunk in wrapper.stream_chat_completion(messages):
                if isinstance(chunk, dict):
                    # 如果是字典，可能是错误信息
                    if "error" in chunk:
                        error_occurred = True
                        error_message = chunk.get("error", "未知错误")
                        status_code = chunk.get("status_code", "unknown")

                        # 显示简化的错误信息
                        if "400" in str(status_code) or "Bad Request" in error_message:
                            placeholder.error("❌ 访问被GPT敏感词过滤，请检查输入内容")
                        elif "401" in str(status_code) or "Unauthorized" in error_message:
                            placeholder.error("❌ API认证失败，请检查API密钥")
                        elif "403" in str(status_code) or "Forbidden" in error_message:
                            placeholder.error("❌ 访问被拒绝，请检查权限设置")
                        elif "500" in str(status_code) or "Internal Server Error" in error_message:
                            placeholder.error("❌ 服务器内部错误，请稍后重试")
                        else:
                            placeholder.error("❌ 网络连接错误，请检查网络设置")
                        break
                    continue
                else:
                    response_text += chunk
                    placeholder.markdown(response_text + "▌")

            if error_occurred:
                return None
            else:
                placeholder.markdown(response_text)
                return response_text

        except Exception as e:
            error_message = str(e)
            if "timeout" in error_message.lower():
                placeholder.error("❌ 请求超时，请稍后重试")
            elif "connection" in error_message.lower():
                placeholder.error("❌ 网络连接失败，请检查网络设置")
            else:
                placeholder.error("❌ 请求处理失败，请稍后重试")
            return None

class ProcessMode:
    """处理模式基类"""
    def __init__(self, wrapper: GPT4OWrapper):
        self.wrapper = wrapper
        self.container = st.container()
        self.placeholder = st.empty()
        self.progress_bar = None
        self.status_text = None

    def initialize_progress(self, title: str):
        """初始化进度组件"""
        st.subheader(title)
        self.progress_bar, self.status_text = UIComponents.create_progress_container(self.container)

    def update_progress(self, value: int, message: str):
        """更新进度状态"""
        self.progress_bar.progress(value)
        self.status_text.text(message)

    def save_result(self, mode: str, result: ProcessResult):
        """保存结果到session state"""
        st.session_state[mode] = result
        st.session_state['has_rerun'] = True

class GuardrailMode(ProcessMode):
    """带安全检测的处理模式"""
    def execute(self, user_input: str):
        """执行处理流程"""
        self.initialize_progress("🛡️ 有Guardrail模式")

        # 阶段1: 安全检测
        self.update_progress(25, "进行安全检测...")
        safety_info, guardrail_latency = SafetyHandler.check_safety(user_input)

        if not safety_info:
            self.save_result('guardrail_result', {
                'input': user_input,
                'error': True,
                'message': '安全检测失败'
            })
            return

        # 显示安全信息
        # st.markdown("### 安全检测结果")
        st.markdown(SafetyHandler.format_safety_info(safety_info))
        st.markdown("CaLLM安全评级: OOD")

        # 阶段2: 生成响应
        # self.update_progress(50, "生成响应...")
        start_time = time.time()
        prompt = self.generate_prompt(user_input, safety_info)
        response = ResponseHandler.stream_response(
            self.wrapper,
            [{"role": "user", "content": prompt}],
            'guardrail_output'  # 使用专属placeholder key
        )
        gpt_latency = (time.time() - start_time) * 1000

        # 处理结果
        self.finalize_process(
            user_input,
            response,
            guardrail_latency,
            gpt_latency,
            safety_info
        )

    def generate_prompt(self, user_input: str, safety_info: SafetyInfo) -> str:
        """生成最终提示"""
        if safety_info.get("User Safety") == "safe":
            return user_input
        return generate_response_prompt(
            user_input,
            safety_info["User Safety"],
            safety_info["Safety Categories"]
        )

    def finalize_process(self, user_input, response, guardrail_latency, gpt_latency, safety_info):
        """完成处理流程"""
        # st.info(f"⏱️ 响应延时: {guardrail_latency:.2f}ms")
        if not response:
            self.save_result('guardrail_result', {
                'input': user_input,
                'error': True,
                'message': 'GPT响应失败'
            })
            return
        self.save_result('guardrail_result', {
            'input': user_input,
            'response': response,
            'latencies': {
                'guardrail': guardrail_latency,
                'gpt': gpt_latency,
                'total': guardrail_latency + gpt_latency
            },
            'safety_info': safety_info,
            'error': False
        })

class DirectMode(ProcessMode):
    """直接处理模式"""
    def execute(self, user_input: str):
        """执行处理流程"""
        self.initialize_progress("🚫 无Guardrail模式")

        # 生成响应
        # self.update_progress(50, "生成响应...")
        start_time = time.time()
        response = ResponseHandler.stream_response(
            self.wrapper,
            [{"role": "user", "content": user_input}],
            'direct_output'  # 使用专属placeholder key
        )
        latency = (time.time() - start_time) * 1000

        # 处理结果
        self.finalize_process(user_input, response, latency)

    def finalize_process(self, user_input, response, latency):
        """完成处理流程"""
        # st.info(f"⏱️ 响应延迟: {latency:.2f}ms")
        if not response:
            self.save_result('direct_result', {
                'input': user_input,
                'error': True,
                'message': 'GPT响应失败'
            })
            return
        self.save_result('direct_result', {
            'input': user_input,
            'response': response,
            'latency': latency,
            'error': False
        })

def main_sidebar(wrapper: GPT4OWrapper):
    """侧边栏组件"""
    with st.sidebar:
        st.header("配置选项")

        # 诊断面板
        with st.expander("🔧 系统诊断", expanded=False):
            if st.button("🔄 检查API状态"):
                with st.spinner("检测中..."):
                    try:
                        test_response = wrapper.chat_completion([{"role": "user", "content": "ping"}])
                        st.success("✅ 服务可用")
                        st.metric("响应时间", f"{test_response[1]:.2f}ms")
                    except Exception as e:
                        st.error(f"❌ 服务不可用: {str(e)}")

        # 示例查询
        with st.expander("📋 示例查询", expanded=True):
            selected = st.selectbox("选择示例", EXAMPLE_QUERIES)
            if st.button("使用示例"):
                st.session_state.clear()
                st.session_state.user_input = selected
                st.rerun()

        # 控制按钮
        if st.button("🔄 清除会话", type="tertiary"):
            st.session_state.clear()
            st.rerun()

def main():
    """主函数"""
    # 应用配置
    st.set_page_config(
        page_title="Guardrails功能对比演示",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 初始化全局组件
    UIComponents.show_header()
    wrapper = get_gpt_wrapper()
    main_sidebar(wrapper)

    # 主内容容器
    with st.container():
        # 用户输入区域
        user_input = st.text_area(
            "📝 请输入您的问题",
            height=80,
            placeholder="例如：如何制作炸药?",
            help="输入需要检测的内容，支持多行文本",
            key="user_input"
        )

        # 模式选择按钮
        direct_btn, guardrail_btn = UIComponents.create_mode_buttons()

        # 双列结果展示区域
        col1, col2 = st.columns(2, gap="large")


        # 左列 - 无Guardrail模式结果
        with col1:
            if direct_btn and user_input:
                DirectMode(wrapper).execute(user_input)

            if 'direct_result' in st.session_state:
                # 清除stream_response的生成结果

                if 'direct_placeholder' in st.session_state:
                    st.session_state.direct_placeholder.empty()
                if 'guardrail_placeholder' in st.session_state:
                    st.session_state.guardrail_placeholder.empty()

                with st.container(border=True):
                    st.subheader("🚫 无Guardrail模式结果")
                    result = st.session_state.direct_result
                    if result['error']:
                        st.error(result['message'])
                    else:
                        # st.info(f"⏱️ GPT延迟: {result['latency']:.2f}ms")
                        st.success(result['response'])

                    if st.session_state.get('has_rerun', False):
                        st.session_state.has_rerun = False
                        print(f"direct_btn: refresh ui proactivately")
                        st.rerun()

        # 右列 - 有Guardrail模式结果
        with col2:
            if guardrail_btn and user_input:
                GuardrailMode(wrapper).execute(user_input)

            if 'guardrail_result' in st.session_state:

                # 清除stream_response的生成结果
                if 'direct_placeholder' in st.session_state:
                    st.session_state.direct_placeholder.empty()
                if 'guardrail_placeholder' in st.session_state:
                    st.session_state.guardrail_placeholder.empty()

                with st.container(border=True):
                    st.subheader("🛡️ 有Guardrail模式结果")
                    result = st.session_state.guardrail_result
                    if result['error']:
                        st.error(result['message'])
                    else:
                        st.markdown(SafetyHandler.format_safety_info(result['safety_info']))
                        st.markdown(SafetyHandler.format_callm_info(result['safety_info']))
                        st.info(f"⏱️ Guardrails延迟: {result['latencies']['guardrail']:.2f}ms")
                        # st.info(f"⏱️ GPT延迟: {result['latencies']['gpt']:.2f}ms")
                        # col_a, col_b, col_c = st.columns(3)
                        # col_a.metric("Guardrails延迟", f"{result['latencies']['guardrail']:.2f}ms")
                        # col_b.metric("GPT延迟", f"{result['latencies']['gpt']:.2f}ms")
                        # col_c.metric("总延迟", f"{result['latencies']['total']:.2f}ms")
                        st.success(result['response'])

                    if st.session_state.get('has_rerun', False):
                        st.session_state.has_rerun = False
                        print(f"guardrail_btn: refresh the UI ")
                        st.rerun()

        # 页脚区域
        UIComponents.show_footer()

if __name__ == "__main__":
    main()