#!/usr/bin/env python3
"""
测试日志功能
运行此脚本查看详细日志输出
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 设置 DEBUG 级别
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['LOG_TO_FILE'] = 'True'

from src.parser import MarkdownParser

# 测试 Markdown 内容
test_md = """
# 测试标题

这是测试内容,用于验证日志功能。

```python
def test():
    print("hello world")
```

![测试图片](https://example.com/test.jpg)

参考链接: [测试链接](https://example.com/article)

更多内容... #测试标签 #Python #AI

> 这是一段引用

---

结束。
"""

print("=" * 70)
print("🧪 测试日志功能")
print("=" * 70)
print()
print("测试内容:")
print(test_md)
print()
print("运行解析器,查看详细日志输出...")
print("=" * 70)
print()

# 运行解析
parser = MarkdownParser()
result = parser.parse(test_md)

print()
print("=" * 70)
print("✅ 解析完成!")
print("=" * 70)
print()
print(f"解析结果:")
print(f"  - 文本块: {len(result.text_blocks)} 个")
print(f"  - 代码块: {len(result.code_blocks)} 个")
print(f"  - 图片: {len(result.images)} 张")
print(f"  - 链接: {len(result.links)} 个")
print(f"  - 标签: {len(result.tags)} 个")
print()
print(f"📝 查看详细日志文件: logs/notebook_tools_*.log")
print()
print("查看命令:")
print(f"  tail -f logs/notebook_tools_*.log")
print(f"  grep '解析结果' logs/*.log")
print()
