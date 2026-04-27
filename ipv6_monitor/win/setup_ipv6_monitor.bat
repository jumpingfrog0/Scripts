@echo off

echo ==================================
echo        IPv6 TASK MANAGER
echo ==================================
echo.
echo CURRENT TASKS:
schtasks /query /fo TABLE | findstr "IPv6"

echo.
echo UPDATING TASKS...

:: Clean old tasks
schtasks /delete /tn "IPv6Monitor_SystemStartup" /f 2>nul
schtasks /delete /tn "IPv6Monitor_PeriodicCheck" /f 2>nul

:: Setup new tasks
schtasks /create /tn "IPv6Monitor_SystemStartup" /tr "C:\Python313\python.exe D:\AutoScripts\ipv6_monitor\ipv6_feishu_monitor.py" /sc ONSTART /delay 0000:30 /ru SYSTEM
schtasks /create /tn "IPv6Monitor_PeriodicCheck" /tr "C:\Python313\python.exe D:\AutoScripts\ipv6_monitor\ipv6_feishu_monitor.py" /sc MINUTE /mo 5 /ru SYSTEM

echo.
echo TASKS CREATED:
echo - IPv6Monitor_SystemStartup (on system startup)
echo - IPv6Monitor_PeriodicCheck (every 5 minutes)

echo.
schtasks /query /fo TABLE | findstr "IPv6"

echo.
echo Press any key to exit...
pause >nul