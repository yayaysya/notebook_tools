# 日志使用说明

## 概述

项目支持详细的日志记录功能,便于调试和问题排查。日志会同时输出到控制台和文件。

## 快速开始

### 启用 DEBUG 日志

**方式 1: 环境变量**
```bash
export LOG_LEVEL=DEBUG
streamlit run app.py
```

**方式 2: .env 文件**
```bash
echo "LOG_LEVEL=DEBUG" >> .env
streamlit run app.py
```

## 配置选项

在 `.env` 文件中配置:

```ini
# 日志级别: DEBUG/INFO/WARNING/ERROR
LOG_LEVEL=DEBUG

# 是否输出到文件 (True/False)
LOG_TO_FILE=True

# 日志目录
LOG_DIR=logs

# 单个日志文件最大大小(MB)
LOG_MAX_SIZE_MB=10

# 保留的日志文件数量
LOG_BACKUP_COUNT=5
```

## 日志级别

| 级别 | 说明 | 输出内容 |
|------|------|---------|
| **DEBUG** | 调试 | 所有详细信息(解析结果、AI请求/响应、Token消耗等) |
| **INFO** | 信息 | 关键步骤和进度信息 |
| **WARNING** | 警告 | 警告信息和可恢复的错误 |
| **ERROR** | 错误 | 错误和异常信息 |

## 日志内容

### DEBUG 级别输出

#### 1. Markdown 解析阶段

```
======================================================================
📄 Markdown 解析结果
======================================================================
原始文件大小: 1234 字符
文本块数量: 5
  文本块[1]: # 测试标题
  文本块[2]: 这是测试内容。
  ...

代码块数量: 1
  代码块[1]:
```python
def test():
    print("hello")
```

图片数量: 2
  图片[1]: https://example.com/img1.jpg (alt: 图片1)
  图片[2]: https://example.com/img2.jpg (alt: 图片2)

链接数量: 1
  链接[1]: 测试链接 -> https://example.com/article

标签: #技术, #Python, #AI
======================================================================
```

#### 2. AI 请求阶段 (需手动添加)

```
----------------------------------------------------------------------
🤖 AI 请求 - 图片识别
----------------------------------------------------------------------
模型: glm-4.5v
图片 URL: https://example.com/image.jpg
Prompt:
请详细描述这张图片的内容...
----------------------------------------------------------------------
```

#### 3. AI 响应阶段 (需手动添加)

```
✅ AI 响应 - 图片识别
耗时: 3.21s
响应内容:
这张图片展示了...

Token 消耗: prompt=150, completion=80, total=230
----------------------------------------------------------------------
```

## 查看日志

### 实时查看最新日志

```bash
tail -f logs/notebook_tools_*.log
```

### 搜索特定内容

```bash
# 查看所有 AI 请求
grep "AI 请求" logs/*.log

# 查看 Token 消耗
grep "Token 消耗" logs/*.log

# 查看错误
grep "ERROR" logs/*.log

# 查看解析结果
grep "解析结果" logs/*.log
```

### 按时间查看

```bash
# 查看今天的日志
ls -lt logs/ | head -5

# 查看最新的日志文件
ls -t logs/*.log | head -1 | xargs cat
```

## 日志文件

### 文件命名

格式: `notebook_tools_YYYYMMDD_HHMMSS.log`

示例:
- `notebook_tools_20251021_143022.log`
- `notebook_tools_20251021_150315.log`

### 文件轮转

- 单个文件最大 10MB (可配置)
- 超过大小自动创建新文件
- 最多保留 5 个历史文件 (可配置)

### 文件位置

默认: `logs/` 目录 (与项目根目录同级)

## 使用场景

### 开发调试

```bash
# 启用 DEBUG 级别
export LOG_LEVEL=DEBUG
streamlit run app.py

# 查看详细日志
tail -f logs/notebook_tools_*.log
```

### 生产运行

```bash
# 使用 INFO 级别
export LOG_LEVEL=INFO
streamlit run app.py
```

### 问题排查

```bash
# 1. 复现问题时启用 DEBUG
export LOG_LEVEL=DEBUG

# 2. 运行出问题的操作

# 3. 查看日志
grep -A 10 "ERROR" logs/*.log

# 4. 查看完整上下文
cat logs/notebook_tools_20251021_*.log
```

## 性能影响

| 级别 | 性能影响 | 建议使用场景 |
|------|---------|-------------|
| DEBUG | 中等 | 开发、调试、问题排查 |
| INFO | 很小 | 生产环境 |
| WARNING | 极小 | 生产环境(仅关注警告) |
| ERROR | 几乎无 | 生产环境(仅关注错误) |

## 常见问题

### Q: 日志文件太多怎么办?

A: 调整配置:
```ini
LOG_BACKUP_COUNT=3  # 只保留3个备份
LOG_MAX_SIZE_MB=5   # 每个文件最大5MB
```

### Q: 不想输出到文件?

A: 设置:
```ini
LOG_TO_FILE=False
```

### Q: 日志太详细,看不清重点?

A: 使用 grep 过滤:
```bash
# 只看关键信息
grep -E "(INFO|ERROR)" logs/*.log

# 只看 AI 相关
grep "AI" logs/*.log
```

### Q: 想自定义日志格式?

A: 修改 `src/logger_util.py` 中的 formatter。

## 示例

完整使用示例见 `tests/test_logging.py`

---

**提示**:
- 开发时使用 `LOG_LEVEL=DEBUG` 查看所有详情
- 生产时使用 `LOG_LEVEL=INFO` 保持性能
- 出问题时查看 `logs/` 目录获取完整上下文
