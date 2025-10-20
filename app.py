"""
Streamlit Web UI
Markdown 笔记智能整理工具的 Web 界面
"""
import streamlit as st
import logging
from pathlib import Path
import sys
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from src.integrator import ContentIntegrator, ProcessingProgress

# 配置日志
logging.basicConfig(
    level=logging.INFO if config.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 页面配置
st.set_page_config(
    page_title="Markdown 笔记智能整理工具",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化 session state"""
    if 'processed_content' not in st.session_state:
        st.session_state.processed_content = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False


def render_sidebar():
    """渲染侧边栏配置"""
    with st.sidebar:
        st.header("⚙️ 配置")

        # API Key 配置
        api_key = st.text_input(
            "智谱 API Key",
            value=config.ZHIPU_API_KEY,
            type="password",
            help="在 https://open.bigmodel.cn/ 获取"
        )

        # 模型配置
        st.subheader("模型设置")
        text_model = st.selectbox(
            "文本模型",
            ["glm-4.6", "glm-4-plus", "glm-4-flash"],
            index=0,
            help="用于内容总结和重组"
        )

        vision_model = st.selectbox(
            "视觉模型",
            ["glm-4.5v", "glm-4v-plus"],
            index=0,
            help="用于图片识别"
        )

        # 高级设置
        with st.expander("高级设置"):
            max_workers = st.slider(
                "并行处理线程数",
                min_value=1,
                max_value=10,
                value=5,
                help="同时处理图片和链接的数量"
            )

        st.divider()

        # 使用说明
        st.subheader("📖 使用说明")
        st.markdown("""
1. 输入智谱 API Key
2. 上传 Markdown 笔记文件
3. 点击「开始处理」
4. 等待 AI 处理完成
5. 预览并下载结果
        """)

        st.divider()

        # 关于信息
        st.caption("基于智谱 AI GLM-4.6 & GLM-4.5V")
        st.caption("v0.1.0")

        return api_key, text_model, vision_model, max_workers


def render_main_content(api_key: str, text_model: str, vision_model: str, max_workers: int):
    """渲染主要内容区域"""

    # 标题
    st.markdown('<div class="main-header">📝 Markdown 笔记智能整理工具</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">将图文混排笔记自动转换为规整的公众号文章</div>',
        unsafe_allow_html=True
    )

    # 文件上传
    uploaded_file = st.file_uploader(
        "上传 Markdown 笔记文件",
        type=['md', 'markdown'],
        help="支持包含图片链接和网页链接的 MD 文件"
    )

    if uploaded_file is not None:
        # 显示原始内容
        original_content = uploaded_file.read().decode('utf-8')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 原始笔记")
            with st.container(height=400):
                st.markdown(original_content)

        with col2:
            st.subheader("✨ 优化后的文章")

            if st.session_state.processed_content:
                with st.container(height=400):
                    st.markdown(st.session_state.processed_content)
            else:
                st.info("点击下方按钮开始处理")

        # 处理按钮
        st.divider()

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

        with col_btn1:
            process_btn = st.button(
                "🚀 开始处理",
                type="primary",
                disabled=st.session_state.processing or not api_key,
                use_container_width=True
            )

        with col_btn2:
            if st.session_state.processed_content:
                st.download_button(
                    label="📥 下载结果",
                    data=st.session_state.processed_content,
                    file_name=f"optimized_{uploaded_file.name}",
                    mime="text/markdown",
                    use_container_width=True
                )

        if not api_key:
            st.warning("⚠️ 请先在侧边栏配置智谱 API Key")

        # 处理逻辑
        if process_btn:
            process_markdown(
                original_content,
                api_key,
                text_model,
                vision_model,
                max_workers
            )

    else:
        # 空状态
        st.info("👆 请上传 Markdown 文件开始使用")

        # 示例展示
        with st.expander("📝 查看示例笔记格式"):
            st.markdown("""
```markdown
# 我的笔记标题

这是一段原始笔记内容,记录了一些想法。

![示例图片](https://example.com/image.jpg)

参考文章: [标题](https://example.com/article)

更多笔记内容...
```
            """)


def process_markdown(
    content: str,
    api_key: str,
    text_model: str,
    vision_model: str,
    max_workers: int
):
    """处理 Markdown 内容"""
    st.session_state.processing = True

    # 更新配置
    config.ZHIPU_API_KEY = api_key
    config.TEXT_MODEL = text_model
    config.VISION_MODEL = vision_model

    # 进度显示
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(prog: ProcessingProgress):
        """进度回调"""
        # 计算总体进度
        total_items = prog.total_images + prog.total_links
        processed_items = prog.processed_images + prog.processed_links

        if total_items > 0:
            progress = processed_items / total_items
        else:
            progress = 0.5

        progress_bar.progress(min(progress, 0.95))
        status_text.text(f"⏳ {prog.current_stage}")

    try:
        # 创建整合器并处理
        integrator = ContentIntegrator(api_key, update_progress)
        result = integrator.process_markdown(content, max_workers)

        # 保存结果
        st.session_state.processed_content = result

        # 完成
        progress_bar.progress(1.0)
        status_text.empty()
        st.success("✅ 处理完成!")
        time.sleep(1)
        st.rerun()

    except Exception as e:
        st.error(f"❌ 处理失败: {str(e)}")
        logging.error(f"处理失败: {str(e)}", exc_info=True)

    finally:
        st.session_state.processing = False


def main():
    """主函数"""
    init_session_state()

    # 渲染侧边栏
    api_key, text_model, vision_model, max_workers = render_sidebar()

    # 渲染主内容
    render_main_content(api_key, text_model, vision_model, max_workers)


if __name__ == "__main__":
    main()
