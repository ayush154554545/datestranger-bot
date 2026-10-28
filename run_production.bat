@echo off
cd /d "%~dp0bot"
if exist mainbot.bat (
    call mainbot.bat %*
) else (
    python bot.py
)
