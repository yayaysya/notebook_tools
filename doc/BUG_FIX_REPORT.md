# Bug 修复报告: 代码块和标签丢失问题

## 问题描述

**症状**: 原始笔记中的代码块(```code```)和 #标签在生成的文章中丢失

**影响范围**:
- ❌ 代码块完全丢失
- ❌ #标签未被识别
- ❌ 引用块(>)可能丢失
- ❌ 分隔线(---)可能丢失
- ❌ 表格可能丢失

## 根本原因

**文件**: `src/parser.py`
**位置**: `_extract_content` 方法 (第 58-125 行)

解析器只处理了以下 token 类型:
- ✅ `paragraph` (段落)
- ✅ `heading` (标题)
- ✅ `list` (列表)
- ✅ `image` (图片)
- ✅ `link` (链接)

**遗漏的类型**:
- ❌ `block_code` (代码块)
- ❌ `block_quote` (引用块)
- ❌ `thematic_break` (分隔线)
- ❌ 标签(需要正则提取)

## 修复方案

### 1. 扩展数据结构

**文件**: `src/parser.py` (第 11-19 行)

```python
@dataclass
class ParsedContent:
    text_blocks: List[str] = field(default_factory=list)
    code_blocks: List[str] = field(default_factory=list)  # 新增
    tags: List[str] = field(default_factory=list)         # 新增
    images: List[Dict[str, str]] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    raw_markdown: str = ""
```

### 2. 添加代码块处理

**文件**: `src/parser.py` (第 82-88 行)

```python
elif token_type == 'block_code':
    # 提取代码块,保留原始格式
    code = token.get('raw', '').strip()
    lang = token.get('info', '')
    code_block = f"```{lang}\n{code}\n```"
    result.code_blocks.append(code_block)
    result.text_blocks.append(code_block)  # 同时加入文本块
```

### 3. 添加引用块和分隔线处理

**文件**: `src/parser.py` (第 90-99 行)

```python
elif token_type == 'block_quote':
    # 提取引用块
    text = self._extract_text(token)
    if text.strip():
        quote_block = f"> {text.strip()}"
        result.text_blocks.append(quote_block)

elif token_type == 'thematic_break':
    # 分隔线
    result.text_blocks.append("---")
```

### 4. 添加标签提取方法

**文件**: `src/parser.py` (第 177-202 行)

```python
def _extract_tags(self, markdown_text: str) -> List[str]:
    """提取 #标签"""
    # 匹配 #标签 格式 (支持中英文、数字、下划线)
    pattern = r'(?:^|[^\w#])(#[\w\u4e00-\u9fa5_]+)'
    matches = re.findall(pattern, markdown_text, re.MULTILINE)

    # 去重并过滤
    seen = set()
    unique_tags = []
    for match in matches:
        tag = match.lstrip('#')
        if tag and not tag.isdigit() and tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags
```

### 5. 更新 AI Prompt

**文件**: `src/zhipu_client.py` (第 158-172 行)

系统提示词新增:
```
8. **重要: 保留所有代码块原样,使用 ```language 格式**
9. **重要: 保留所有引用块(>)、分隔线(---)等特殊格式**
```

用户提示词新增标签信息:
```python
if tags:
    prompt_parts.append("\n## 文章标签\n")
    prompt_parts.append("标签: " + ", ".join([f"#{tag}" for tag in tags]))
    prompt_parts.append("\n请在文章末尾添加标签行。\n")
```

### 6. 更新整合引擎

**文件**: `src/integrator.py` (第 206-218 行)

```python
def _reorganize_content(
    self,
    parsed: ParsedContent,  # 传入完整对象
    images_desc: list,
    links_summary: list
) -> str:
    return self.ai_client.reorganize_article(
        original_text=parsed.text_blocks,
        images_desc=images_desc,
        links_summary=links_summary,
        tags=parsed.tags  # 传递标签
    )
```

## 修改文件清单

| 文件 | 修改内容 | 行数变化 |
|------|---------|---------|
| `src/parser.py` | 扩展数据结构、添加代码块/引用块/标签处理 | +45 行 |
| `src/zhipu_client.py` | 更新 AI Prompt、添加标签参数 | +15 行 |
| `src/integrator.py` | 传递 ParsedContent 对象和标签 | +3 行 |
| `tests/test_parser.py` | 添加代码块、标签、引用块测试 | +55 行 |

**总计**: 4 个文件,新增约 118 行代码

## 测试覆盖

新增测试用例:

1. ✅ `test_parse_code_blocks` - 代码块提取
2. ✅ `test_parse_tags` - #标签识别
3. ✅ `test_parse_block_quote` - 引用块保留
4. ✅ `test_parse_thematic_break` - 分隔线保留
5. ✅ `test_complex_document` - 复杂文档综合测试
6. ✅ `test_tags_not_in_heading` - 避免误识别标题为标签

## 修复效果

### 修复前

```markdown
输入:
# 笔记
一些内容
```python
code
```
更多内容 #标签

输出:
# 笔记
一些内容
更多内容
```
❌ 代码块丢失
❌ 标签丢失

### 修复后

```markdown
输入:
# 笔记
一些内容
```python
code
```
更多内容 #标签

输出:
# 笔记
一些内容

```python
code
```

更多内容

标签: #标签
```
✅ 代码块完整保留
✅ 标签正确识别

## 验证步骤

1. 解析带代码块和标签的 MD 文件
2. 检查 `ParsedContent.code_blocks` 和 `ParsedContent.tags`
3. 验证代码块同时存在于 `text_blocks` 中
4. 确认 AI 重组时收到标签信息
5. 检查最终输出包含代码块和标签

## 兼容性

- ✅ 向后兼容 - 原有功能不受影响
- ✅ 数据结构扩展 - 新增字段有默认值
- ✅ API 兼容 - `reorganize_article` 的 `tags` 参数可选

## 注意事项

1. **标签识别规则**:
   - 支持中英文、数字、下划线
   - 排除纯数字(避免误匹配)
   - 避免误识别 Markdown 标题(#)

2. **代码块保留**:
   - 保留语言标识符
   - 保留原始格式和缩进
   - 同时加入 `code_blocks` 和 `text_blocks`

3. **AI 处理**:
   - System prompt 明确要求保留特殊格式
   - User prompt 包含标签信息
   - AI 需要在文章末尾添加标签行

## 后续优化建议

1. 📋 添加表格(table)的完整支持
2. 🎨 支持更多 Markdown 扩展语法
3. 🧪 增加更多边界情况测试
4. 📊 添加代码块语言统计

## 修复完成 ✅

**修复时间**: 2025-10-21
**版本**: v0.1.1
**状态**: 已完成并测试

---

所有代码块、标签、引用块和分隔线现在都能正确保留! 🎉
