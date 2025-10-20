"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Config:
    """应用配置"""

    # 智谱 AI 配置
    ZHIPU_API_KEY: str = os.getenv("ZHIPU_API_KEY", "")
    TEXT_MODEL: str = os.getenv("TEXT_MODEL", "glm-4.6")
    VISION_MODEL: str = os.getenv("VISION_MODEL", "glm-4.5v")

    # 请求配置
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES: int = 3

    # 日志配置
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Jina AI Reader (无需 API Key 的免费服务)
    JINA_READER_BASE: str = "https://r.jina.ai/"

    @classmethod
    def validate(cls) -> bool:
        """验证必需的配置项"""
        if not cls.ZHIPU_API_KEY:
            return False
        return True

    @classmethod
    def get_error_message(cls) -> str:
        """获取配置错误信息"""
        if not cls.ZHIPU_API_KEY:
            return "未设置 ZHIPU_API_KEY,请在 .env 文件中配置或通过 UI 输入"
        return ""


# 全局配置实例
config = Config()
