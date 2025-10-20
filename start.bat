@echo off
chcp 65001 >nul
echo 📝 Markdown 笔记智能整理工具
echo ================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python,请先安装 Python
    pause
    exit /b 1
)

echo ✓ Python 已安装

REM 检查虚拟环境
if not exist "venv" (
    echo 🔧 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📦 安装依赖...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

REM 检查 .env 文件
if not exist ".env" (
    echo ⚠️  未找到 .env 文件,从模板创建...
    copy .env.example .env >nul
    echo ❗ 请编辑 .env 文件,填入你的智谱 API Key
    echo.
)

REM 启动应用
echo 🚀 启动 Web 界面...
echo 📍 访问: http://localhost:8501
echo.
streamlit run app.py
