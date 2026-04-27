@echo off
chcp 65001 >nul
echo ========================================
echo    现有数据磁盘自动挂载工具
echo ========================================
echo.
echo 功能：挂载已有数据的磁盘（不格式化）
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误：请以管理员身份运行此批处理！
    echo 右键点击选择"以管理员身份运行"
    pause
    exit /b 1
)

:: 运行 PowerShell 脚本
echo 正在运行磁盘挂载脚本...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0Mount-ExistingDisk.ps1"

pause