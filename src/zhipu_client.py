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
        links_summary: List[Dict[str, str]],
        tags: List[str] = None,
        front_matter: Optional[str] = None
    ) -> str:
        """
        使用 GLM-4.6 重组文章

        Args:
            original_text: 原始文本块列表
            images_desc: 图片描述列表 [{"url": "...", "description": "..."}]
            links_summary: 链接总结列表 [{"url": "...", "title": "...", "summary": "..."}]
            tags: 标签列表 (可选)
            front_matter: YAML Front Matter (可选)

        Returns:
            str: 重组后的 Markdown 文章
        """
        # 构建提示词
        prompt = self._build_reorganize_prompt(original_text, images_desc, links_summary, tags, front_matter)

        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {
                        "role": "system",
                        "content": """# 角色与目标 你现在是一位拥有10年一线开发经验的资深工程师，你正在为一个技术博客或团队内部分享撰写一篇文章。你的目标不是编写一份冷冰冰的官方文档，而是像与一位聪明的同事进行技术交流一样，生动、深入地分享你在某个具体技术点上的实践经验、踩坑记录和深度思考。

# 核心写作心态

分享者，非说教者： 你不是在教授知识，而是在分享一段亲身经历的探索旅程。坦诚地展示你的思考过程，包括那些最初的错误假设和走过的弯路。
过程重于结果： 最终的解决方案固然重要，但“如何一步步找到这个方案”的思考路径对读者更有启发价值。
享受复盘： 把这次写作看作一次对过往项目的复盘和沉淀，享受把复杂问题抽丝剥茧、讲清楚的乐趣。

# 具体风格要求

第一人称视角： 全文必须使用“我”或“我们”，让文章充满个人色彩。
口语化表达： 让语言流畅自然，像聊天一样，避免生硬的书面语和“首先、其次、综上所述”这类模板化的词语。
公众号风格： 在保持技术深度的同时，注意排版的美观性，用小标题和重点标记（如加粗）来分解长段落，提升阅读体验。

# 硬性格式规则 (必须严格遵守)

1. **保持原意：** 绝对忠实于原始笔记的核心信息和技术事实，不添加笔记中没有的技术信息。
2. 合理组织结构(可添加小标题)
3. 在合适位置插入图片和引用链接
4. 输出 Markdown 格式
5. 图片格式: ![描述](原始URL)
6. 链接格式: [标题](原始URL)
7. **重要: 保留所有代码块原样,使用 ```language 格式**
8. **重要: 保留所有引用块(>)、分隔线(---)等特殊格式**
9. **重要: 如果有 YAML Front Matter,必须从文章第一行开始,前面不能有空行**
10. 适合公众号发布风格"""
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
            # 移除开头的空行(如果存在),但保留 YAML Front Matter
            result = result.lstrip('\n')
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
        links_summary: List[Dict[str, str]],
        tags: List[str] = None,
        front_matter: Optional[str] = None
    ) -> str:
        """构建文章重组的提示词"""

        prompt_parts = ["请将以下笔记内容整理成一篇完整的文章:\n"]

        # Front Matter
        if front_matter:
            prompt_parts.append("\n## 文章元数据 (YAML Front Matter)\n")
            prompt_parts.append("```yaml\n")
            prompt_parts.append(front_matter)
            prompt_parts.append("\n```\n")
            prompt_parts.append("**重要: 在输出文章的第一行就开始写 YAML Front Matter,格式为:**\n")
            prompt_parts.append("```\n---\n<YAML内容>\n---\n```\n")
            prompt_parts.append("**注意: 输出时 --- 必须从第一行开始,前面不能有任何空行!**\n")

        # 原始文本
        prompt_parts.append("\n## 原始笔记内容\n")
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

        # 标签信息
        if tags:
            prompt_parts.append("\n## 文章标签\n")
            prompt_parts.append("标签: " + ", ".join([f"#{tag}" for tag in tags]))
            prompt_parts.append("\n请在文章末尾添加标签行。\n")

        prompt_parts.append("""
\n请你:
1. 将这些内容整合成一篇连贯的文章
2. 在合适的位置插入图片,格式: ![图片描述](图片URL)
3. 在合适的位置引用链接,格式: [链接标题](链接URL) 或在文末添加"参考链接"部分
4. **保留所有代码块、引用块、分隔线等特殊格式,不要修改**
5. 优化语言表达,但不改变核心意思
6. 输出完整的 Markdown 格式文章
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
