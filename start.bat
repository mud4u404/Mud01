@echo off
chcp 65001 >nul
title 镖局MUD
cd /d "%~dp0"

echo 正在检查 Python...
py --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [错误] 未检测到 Python。
    echo 请前往 https://python.org/downloads 下载安装，
    echo 安装时务必勾选 "Add Python to PATH"。
    pause
    exit /b 1
)

echo 正在安装依赖...
py -m pip install flask rich -q

echo.
echo 游戏启动中...
echo 请在浏览器打开：http://localhost:5000
echo 按 Ctrl+C 可停止服务器。
echo.
start "" http://localhost:5000
py server.py
pause
