"""
Markdown 解析器模块
使用 mistune 解析 MD 文件,提取文本、图片和链接
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
import mistune


@dataclass
class ParsedContent:
    """解析后的内容结构"""
    text_blocks: List[str] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    raw_markdown: str = ""


class MarkdownParser:
    """Markdown 解析器"""

    def __init__(self):
        self.markdown = mistune.create_markdown(
            renderer=None,  # 使用 AST 而不是 HTML
            plugins=['strikethrough', 'table', 'url']
        )

    def parse(self, markdown_text: str) -> ParsedContent:
        """
        解析 Markdown 文本

        Args:
            markdown_text: Markdown 原始文本

        Returns:
            ParsedContent: 解析后的结构化内容
        """
        result = ParsedContent(raw_markdown=markdown_text)

        # 使用 mistune 解析为 AST
        tokens = self.markdown(markdown_text)

        # 递归提取内容
        self._extract_content(tokens, result)

        # 额外使用正则表达式捕获可能遗漏的图片和链接
        self._extract_with_regex(markdown_text, result)

        # 去重
        result.images = self._deduplicate_items(result.images, key='url')
        result.links = self._deduplicate_items(result.links, key='url')

        return result

    def _extract_content(self, tokens: List, result: ParsedContent, context: str = ""):
        """递归提取 tokens 中的内容"""
        for token in tokens:
            token_type = token.get('type', '')

            if token_type == 'paragraph':
                # 提取段落文本
                text = self._extract_text(token)
                if text.strip():
                    result.text_blocks.append(text.strip())
                    context = text.strip()[:100]  # 保留前100字符作为上下文

            elif token_type == 'heading':
                # 提取标题文本
                text = self._extract_text(token)
                if text.strip():
                    result.text_blocks.append(f"# {text.strip()}")

            elif token_type == 'list':
                # 提取列表文本
                text = self._extract_text(token)
                if text.strip():
                    result.text_blocks.append(text.strip())

            elif token_type == 'image':
                # 提取图片
                url = token.get('src', '')
                alt = token.get('alt', '')
                if url:
                    result.images.append({
                        'url': url,
                        'alt': alt,
                        'context': context
                    })

            elif token_type == 'link':
                # 提取链接
                url = token.get('link', '')
                title = self._extract_text(token)
                if url and self._is_webpage_url(url):
                    result.links.append({
                        'url': url,
                        'title': title,
                        'context': context
                    })

            # 递归处理子节点
            if 'children' in token:
                self._extract_content(token['children'], result, context)

    def _extract_text(self, token: Dict) -> str:
        """从 token 中提取纯文本"""
        if token.get('type') == 'text':
            return token.get('raw', '')

        text_parts = []
        if 'children' in token:
            for child in token['children']:
                text_parts.append(self._extract_text(child))

        return ' '.join(text_parts)

    def _extract_with_regex(self, markdown_text: str, result: ParsedContent):
        """使用正则表达式补充提取图片和链接"""

        # 提取图片: ![alt](url)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(image_pattern, markdown_text):
            alt, url = match.groups()
            # 检查是否已存在
            if not any(img['url'] == url for img in result.images):
                result.images.append({
                    'url': url,
                    'alt': alt,
                    'context': self._get_surrounding_text(markdown_text, match.start())
                })

        # 提取链接: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, markdown_text):
            title, url = match.groups()
            if self._is_webpage_url(url) and not any(link['url'] == url for link in result.links):
                result.links.append({
                    'url': url,
                    'title': title,
                    'context': self._get_surrounding_text(markdown_text, match.start())
                })

    def _get_surrounding_text(self, text: str, position: int, radius: int = 100) -> str:
        """获取指定位置周围的文本作为上下文"""
        start = max(0, position - radius)
        end = min(len(text), position + radius)
        context = text[start:end].strip()
        # 移除 markdown 语法
        context = re.sub(r'[#*_\[\]()!]', '', context)
        return context[:100]

    @staticmethod
    def _is_webpage_url(url: str) -> bool:
        """判断是否为网页 URL (排除图片、锚点等)"""
        if not url:
            return False

        # 排除锚点链接
        if url.startswith('#'):
            return False

        # 排除常见图片格式
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        if any(url.lower().endswith(ext) for ext in image_extensions):
            return False

        # 必须是 http/https 协议
        return url.startswith('http://') or url.startswith('https://')

    @staticmethod
    def _deduplicate_items(items: List[Dict], key: str) -> List[Dict]:
        """根据指定 key 去重"""
        seen = set()
        unique_items = []
        for item in items:
            value = item.get(key)
            if value and value not in seen:
                seen.add(value)
                unique_items.append(item)
        return unique_items


def parse_markdown_file(file_path: str) -> ParsedContent:
    """
    解析 Markdown 文件的便捷函数

    Args:
        file_path: MD 文件路径

    Returns:
        ParsedContent: 解析结果
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parser = MarkdownParser()
    return parser.parse(content)


if __name__ == "__main__":
    # 测试代码
    test_md = """
# 测试标题

这是一段测试文本。

![测试图片](https://example.com/image.jpg)

这里有一个[测试链接](https://example.com/article)。

- 列表项 1
- 列表项 2
"""

    parser = MarkdownParser()
    result = parser.parse(test_md)

    print("文本块:", result.text_blocks)
    print("图片:", result.images)
    print("链接:", result.links)
