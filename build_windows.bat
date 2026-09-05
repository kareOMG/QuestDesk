@echo off
chcp 65001 >nul
title QuestDesk Windows 打包工具

echo ========================================================
echo               QuestDesk Windows 独立应用打包
echo ========================================================
echo.

set "PY_BIN=C:\Users\28346\AppData\Local\Programs\Python\Python312\python.exe"

if not exist "%PY_BIN%" (
    set "PY_BIN=python"
)

echo [1/3] 检查构建环境与 PyInstaller...
"%PY_BIN%" -m pip install pyinstaller PySide6 -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [2/3] 正在使用 PyInstaller 编译打包...
"%PY_BIN%" -m PyInstaller --noconfirm --clean QuestDesk.spec

echo.
echo [3/3] 复制初始数据配置...
if not exist "dist\QuestDesk\data" mkdir "dist\QuestDesk\data"
if exist "data\okr_data.json" (
    copy /y "data\okr_data.json" "dist\QuestDesk\data\okr_data.json" >nul
)

echo.
echo ========================================================
echo   打包成功！
echo   可执行文件位于: dist\QuestDesk\QuestDesk.exe
echo ========================================================
pause
