# Markdown 笔记智能整理工具

基于智谱 AI GLM-4.6 和 GLM-4.5V 的图文混排笔记自动化整理方案,可将原始 Markdown 笔记快速转换为规整的公众号文章。

## ✨ 功能特点

- 🔍 **自动解析** - 智能识别 Markdown 中的文本、图片和链接
- 👁️ **视觉理解** - 使用 GLM-4.5V 识别图片内容,无需下载图片
- 🌐 **链接抓取** - 自动抓取和总结网页内容(双重策略保障成功率)
- 🤖 **AI 重组** - 利用 GLM-4.6 的 200K 上下文智能重组文章
- 📝 **格式优化** - 自动插入图片和引用,输出适合公众号的格式
- 🚀 **并行处理** - 多线程同时处理图片和链接,效率更高
- 💻 **简洁界面** - Streamlit Web UI,无需命令行操作

## 🏗️ 技术架构

```
输入 MD 笔记
     ↓
Markdown 解析器 (mistune)
     ↓
  并行处理
 ↙        ↘
图片识别    网页抓取+总结
(GLM-4.5V)  (readability/Jina + GLM-4.6)
 ↘        ↙
 内容整合引擎
     ↓
GLM-4.6 重组 (200K 上下文)
     ↓
输出优化文章
```

### 核心技术

- **AI 模型**: 智谱 GLM-4.6 (文本) + GLM-4.5V (视觉)
- **Web 框架**: Streamlit
- **解析器**: mistune (Markdown AST)
- **网页抓取**: requests + readability-lxml (主) + Jina AI Reader (备)

## 📦 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd notebook_tools
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

复制环境变量模板:

```bash
cp .env.example .env
```

编辑 `.env` 文件,填入你的智谱 API Key:

```ini
ZHIPU_API_KEY=your_api_key_here
```

> 💡 在 [智谱 AI 开放平台](https://open.bigmodel.cn/) 注册并获取 API Key

## 🚀 使用方法

### 启动 Web 界面

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

### 使用步骤

1. **配置 API Key** (侧边栏)
   - 输入智谱 API Key
   - 可选择模型和调整参数

2. **上传笔记文件**
   - 点击上传按钮
   - 选择你的 `.md` 文件

3. **开始处理**
   - 点击「开始处理」按钮
   - 实时查看处理进度

4. **预览和下载**
   - 左侧显示原始笔记
   - 右侧预览优化后的文章
   - 点击「下载结果」保存

## 📄 示例笔记格式

```markdown
# 人工智能发展趋势

最近看到一些关于 AI 的有趣内容。

![AI 技术图](https://example.com/ai-tech.jpg)

这篇文章很有启发: [大模型的未来](https://example.com/article)

我的一些思考:
- 多模态是趋势
- 长文本能力很重要

![另一张图](https://example.com/chart.jpg)

总结...
```

**处理后效果:**

- 图片会被 AI 识别内容并添加描述
- 链接会被总结并自然融入文章
- 语言表达得到优化
- 结构更加清晰连贯

## 🔧 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ZHIPU_API_KEY` | 智谱 API 密钥 | 必填 |
| `TEXT_MODEL` | 文本模型 | `glm-4.6` |
| `VISION_MODEL` | 视觉模型 | `glm-4.5v` |
| `REQUEST_TIMEOUT` | 请求超时(秒) | `30` |
| `DEBUG` | 调试模式 | `False` |

### 模型选择

**文本模型:**
- `glm-4.6` (推荐) - 200K 上下文,Token 省 30%
- `glm-4-plus` - 更强能力
- `glm-4-flash` - 更快速度

**视觉模型:**
- `glm-4.5v` (推荐) - MOE 架构,支持 URL
- `glm-4v-plus` - 更强视觉理解

## 🛠️ 开发

### 项目结构

```
notebook_tools/
├── app.py              # Streamlit 主应用
├── config.py           # 配置管理
├── requirements.txt    # 依赖
├── .env.example        # 环境变量模板
├── src/
│   ├── __init__.py
│   ├── parser.py       # Markdown 解析器
│   ├── zhipu_client.py # 智谱 AI 客户端
│   ├── web_scraper.py  # 网页抓取
│   └── integrator.py   # 内容整合引擎
├── tests/
│   └── test_parser.py  # 单元测试
└── examples/
    └── sample_note.md  # 示例文件
```

### 运行测试

```bash
python -m pytest tests/
```

### 单独测试模块

```bash
# 测试解析器
python src/parser.py

# 测试智谱客户端
python src/zhipu_client.py

# 测试网页抓取
python src/web_scraper.py
```

## 📝 工作原理

### 1. Markdown 解析

使用 `mistune` 解析 Markdown 为 AST,提取:
- 文本块(段落、标题、列表)
- 图片链接及上下文
- 网页链接及上下文

### 2. 并行处理

**图片识别:**
- GLM-4.5V 直接读取图片 URL(无需下载)
- 生成简洁的图片描述

**链接抓取:**
- 优先使用 readability-lxml(快速、本地)
- 失败时自动降级到 Jina AI Reader(云服务)
- GLM-4.6 总结网页核心内容

### 3. 内容整合

将原始文本、图片描述、链接总结组合,通过 GLM-4.6 的 200K 上下文一次性处理,生成:
- 结构优化的文章
- 自然插入的图片
- 恰当引用的链接
- 流畅的语言表达

## 🔍 网页抓取策略

采用**双重策略**确保成功率:

1. **主策略: readability-lxml**
   - 快速、轻量
   - 适合静态网页
   - 本地处理,无需外部服务

2. **备用策略: Jina AI Reader**
   - 云服务,零配置
   - 支持复杂网页
   - 免费额度充足

自动在两种方案间切换,最大化成功率。

## 💡 使用技巧

1. **图片要求**
   - 使用网络图片 URL(https://)
   - 确保图片可公开访问

2. **链接要求**
   - 使用完整的 URL(包含 http/https)
   - 优先选择正规网站内容

3. **笔记组织**
   - 保持基本结构(标题、段落)
   - 原始文本可以简略
   - AI 会自动优化表达

4. **性能优化**
   - 调整「并行处理线程数」
   - 建议 5-10 之间
   - 过多可能触发 API 限流

## ⚠️ 注意事项

- **API 成本**: 每次处理会调用多次 AI,注意费用
- **图片访问**: 确保图片 URL 可访问,否则识别失败
- **网页抓取**: 部分网站有反爬虫,可能抓取失败
- **内容长度**: 超长笔记可能超出 token 限制

## 📊 性能参考

典型笔记(5 段文字 + 3 张图 + 2 个链接):
- 处理时间: 约 30-60 秒
- Token 消耗: 约 3000-5000 tokens
- 成功率: 95%+ (图片和链接可访问时)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

## 🔗 相关链接

- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [GLM-4.6 文档](https://docs.bigmodel.cn/cn/guide/models/text/glm-4.6)
- [GLM-4.5V 文档](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.5v)

---

**如有问题或建议,欢迎提 Issue!** 🎉
