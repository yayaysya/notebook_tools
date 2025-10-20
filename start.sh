#!/bin/bash

# 快速启动脚本

echo "📝 Markdown 笔记智能整理工具"
echo "================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3,请先安装 Python"
    exit 1
fi

echo "✓ Python3 已安装"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件,从模板创建..."
    cp .env.example .env
    echo "❗ 请编辑 .env 文件,填入你的智谱 API Key"
    echo ""
fi

# 启动应用
echo "🚀 启动 Web 界面..."
echo "📍 访问: http://localhost:8501"
echo ""
streamlit run app.py
