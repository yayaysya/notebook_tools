"""
智谱 AI 客户端封装
支持 GLM-4.6 (文本) 和 GLM-4.5V (视觉)
"""
from typing import Optional, Dict, List
import logging
from zhipuai import ZhipuAI
from config import config

logger = logging.getLogger(__name__)


class ZhipuClient:
    """智谱 AI 客户端封装"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: API 密钥,如果不提供则从配置读取
        """
        self.api_key = api_key or config.ZHIPU_API_KEY
        if not self.api_key:
            raise ValueError("未提供智谱 API Key")

        self.client = ZhipuAI(api_key=self.api_key)
        self.text_model = config.TEXT_MODEL
        self.vision_model = config.VISION_MODEL

    def analyze_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """
        使用 GLM-4.5V 分析图片内容

        Args:
            image_url: 图片 URL (支持网络链接)
            prompt: 自定义提示词,不提供则使用默认

        Returns:
            str: 图片内容描述
        """
        if not prompt:
            prompt = """请详细描述这张图片的内容,包括:
1. 主要对象或主题
2. 视觉元素(颜色、布局、风格等)
3. 图片传达的信息或情感

请用简洁专业的语言,适合插入到文章中作为图片说明。"""

        try:
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            result = response.choices[0].message.content
            logger.info(f"成功分析图片: {image_url[:50]}...")
            return result

        except Exception as e:
            logger.error(f"图片分析失败 ({image_url}): {str(e)}")
            return f"[图片分析失败: {str(e)}]"

    def summarize_text(self, text: str, context: Optional[str] = None) -> str:
        """
        使用 GLM-4.6 总结文本内容

        Args:
            text: 需要总结的文本
            context: 上下文信息

        Returns:
            str: 总结结果
        """
        prompt = f"""请对以下网页内容进行总结,提取核心信息:

{text}

要求:
1. 保留关键观点和重要信息
2. 语言简洁流畅
3. 适合融入文章叙述
4. 控制在 200 字以内
"""

        if context:
            prompt = f"上下文: {context}\n\n" + prompt

        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的内容总结助手,擅长提炼核心信息。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=800
            )

            result = response.choices[0].message.content
            logger.info(f"成功总结文本 ({len(text)} 字 -> {len(result)} 字)")
            return result

        except Exception as e:
            logger.error(f"文本总结失败: {str(e)}")
            return f"[总结失败: {str(e)}]"

    def reorganize_article(
        self,
        original_text: List[str],
        images_desc: List[Dict[str, str]],
        links_summary: List[Dict[str, str]]
    ) -> str:
        """
        使用 GLM-4.6 重组文章

        Args:
            original_text: 原始文本块列表
            images_desc: 图片描述列表 [{"url": "...", "description": "..."}]
            links_summary: 链接总结列表 [{"url": "...", "title": "...", "summary": "..."}]

        Returns:
            str: 重组后的 Markdown 文章
        """
        # 构建提示词
        prompt = self._build_reorganize_prompt(original_text, images_desc, links_summary)

        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的内容编辑,擅长将零散的笔记整理成结构清晰、语言流畅的文章。

要求:
1. 保持原意,不添加原文没有的信息
2. 优化语言表达,使文章连贯自然
3. 合理组织结构(可添加小标题)
4. 在合适位置插入图片和引用链接
5. 输出 Markdown 格式
6. 图片格式: ![描述](原始URL)
7. 链接格式: [标题](原始URL)
8. 适合公众号发布风格"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.6,
                max_tokens=4000
            )

            result = response.choices[0].message.content
            logger.info(f"成功重组文章 (输出 {len(result)} 字)")
            return result

        except Exception as e:
            logger.error(f"文章重组失败: {str(e)}")
            # 返回原始内容作为后备
            return "\n\n".join(original_text)

    def _build_reorganize_prompt(
        self,
        original_text: List[str],
        images_desc: List[Dict[str, str]],
        links_summary: List[Dict[str, str]]
    ) -> str:
        """构建文章重组的提示词"""

        prompt_parts = ["请将以下笔记内容整理成一篇完整的文章:\n"]

        # 原始文本
        prompt_parts.append("## 原始笔记内容\n")
        for i, text in enumerate(original_text, 1):
            prompt_parts.append(f"{i}. {text}\n")

        # 图片信息
        if images_desc:
            prompt_parts.append("\n## 可用图片素材\n")
            for i, img in enumerate(images_desc, 1):
                prompt_parts.append(
                    f"{i}. 图片URL: {img['url']}\n"
                    f"   描述: {img['description']}\n"
                )

        # 链接信息
        if links_summary:
            prompt_parts.append("\n## 参考链接信息\n")
            for i, link in enumerate(links_summary, 1):
                prompt_parts.append(
                    f"{i}. 标题: {link['title']}\n"
                    f"   URL: {link['url']}\n"
                    f"   内容总结: {link['summary']}\n"
                )

        prompt_parts.append("""
\n请你:
1. 将这些内容整合成一篇连贯的文章
2. 在合适的位置插入图片,格式: ![图片描述](图片URL)
3. 在合适的位置引用链接,格式: [链接标题](链接URL) 或在文末添加"参考链接"部分
4. 优化语言表达,但不改变核心意思
5. 输出完整的 Markdown 格式文章
""")

        return "".join(prompt_parts)


# 便捷函数
def create_client(api_key: Optional[str] = None) -> ZhipuClient:
    """创建智谱 AI 客户端"""
    return ZhipuClient(api_key)


if __name__ == "__main__":
    # 测试代码
    import os
    from dotenv import load_dotenv

    load_dotenv()

    client = create_client()
    print("智谱 AI 客户端初始化成功")
    print(f"文本模型: {client.text_model}")
    print(f"视觉模型: {client.vision_model}")
