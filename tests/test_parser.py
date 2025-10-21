"""
测试 Markdown 解析器
"""
import unittest
from src.parser import MarkdownParser


class TestMarkdownParser(unittest.TestCase):
    """测试 Markdown 解析器"""

    def setUp(self):
        self.parser = MarkdownParser()

    def test_parse_text(self):
        """测试文本提取"""
        md = "# 标题\n\n这是一段文本。"
        result = self.parser.parse(md)
        self.assertGreater(len(result.text_blocks), 0)

    def test_parse_images(self):
        """测试图片提取"""
        md = "![alt text](https://example.com/image.jpg)"
        result = self.parser.parse(md)
        self.assertEqual(len(result.images), 1)
        self.assertEqual(result.images[0]['url'], "https://example.com/image.jpg")

    def test_parse_links(self):
        """测试链接提取"""
        md = "[链接标题](https://example.com/article)"
        result = self.parser.parse(md)
        self.assertEqual(len(result.links), 1)
        self.assertEqual(result.links[0]['url'], "https://example.com/article")

    def test_ignore_image_links(self):
        """测试排除图片链接"""
        md = "[图片链接](https://example.com/image.jpg)"
        result = self.parser.parse(md)
        # 图片链接不应该被作为普通链接
        self.assertEqual(len(result.links), 0)

    def test_parse_code_blocks(self):
        """测试代码块提取"""
        md = "```python\nprint('hello')\n```"
        result = self.parser.parse(md)
        self.assertEqual(len(result.code_blocks), 1)
        self.assertIn("print('hello')", result.code_blocks[0])
        # 代码块应该同时在 text_blocks 中
        self.assertTrue(any("print('hello')" in block for block in result.text_blocks))

    def test_parse_tags(self):
        """测试标签提取"""
        md = "这是内容 #技术 #AI #Python"
        result = self.parser.parse(md)
        self.assertEqual(len(result.tags), 3)
        self.assertIn("技术", result.tags)
        self.assertIn("AI", result.tags)
        self.assertIn("Python", result.tags)

    def test_parse_block_quote(self):
        """测试引用块"""
        md = "> 这是引用"
        result = self.parser.parse(md)
        self.assertGreater(len(result.text_blocks), 0)
        # 检查是否包含引用格式
        self.assertTrue(any(">" in block for block in result.text_blocks))

    def test_parse_thematic_break(self):
        """测试分隔线"""
        md = "段落1\n\n---\n\n段落2"
        result = self.parser.parse(md)
        # 分隔线应该被保留
        self.assertTrue(any("---" in block for block in result.text_blocks))

    def test_complex_document(self):
        """测试复杂文档"""
        md = """
# 标题

段落1

```python
def test():
    pass
```

![图片1](https://example.com/img1.jpg)

段落2 [链接1](https://example.com/link1) #标签1

> 引用内容

- 列表项1
- 列表项2

---

![图片2](https://example.com/img2.jpg)

#标签2 #标签3
"""
        result = self.parser.parse(md)
        self.assertGreater(len(result.text_blocks), 0)
        self.assertEqual(len(result.images), 2)
        self.assertEqual(len(result.links), 1)
        self.assertEqual(len(result.code_blocks), 1)
        self.assertGreaterEqual(len(result.tags), 2)

    def test_tags_not_in_heading(self):
        """测试避免将标题误识别为标签"""
        md = "# 这是标题\n\n正文 #真正的标签"
        result = self.parser.parse(md)
        # 应该只识别出一个标签
        self.assertEqual(len(result.tags), 1)
        self.assertEqual(result.tags[0], "真正的标签")


if __name__ == '__main__':
    unittest.main()
