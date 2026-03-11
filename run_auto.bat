@echo off
chcp 65001 >nul
REM ===================================================================
REM 场地预约自动运行脚本
REM ===================================================================
REM 此脚本会持续运行，每隔指定时间执行一次预约程序
REM 按 Ctrl+C 可以停止脚本运行
REM ===================================================================

echo ========================================
echo 场地预约自动运行脚本
echo ========================================
echo.

REM 设置运行间隔时间（秒）
REM 默认为 1800 秒（30分钟）
REM 可根据需要修改此值
set INTERVAL=1800

REM 激活 conda 环境（如果你使用 conda）
REM 如果不使用 conda，可以注释掉下面这行
call D:\anaconda\shell\condabin\conda-hook.ps1 >nul 2>&1
call conda activate torch >nul 2>&1

:LOOP
echo.
echo [%date% %time%] 开始执行预约程序...
echo ----------------------------------------

REM 运行 Python 程序
python cgyy.py

echo.
echo [%date% %time%] 程序执行完成
echo 等待 %INTERVAL% 秒后再次运行...
echo ========================================
echo.

REM 等待指定时间
timeout /t %INTERVAL% /nobreak

REM 继续循环
goto LOOP
