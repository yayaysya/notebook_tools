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

    def test_complex_document(self):
        """测试复杂文档"""
        md = """
# 标题

段落1

![图片1](https://example.com/img1.jpg)

段落2 [链接1](https://example.com/link1)

- 列表项1
- 列表项2

![图片2](https://example.com/img2.jpg)
"""
        result = self.parser.parse(md)
        self.assertGreater(len(result.text_blocks), 0)
        self.assertEqual(len(result.images), 2)
        self.assertEqual(len(result.links), 1)


if __name__ == '__main__':
    unittest.main()
