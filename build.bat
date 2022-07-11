@echo off
pipenv run pyinstaller main.spec
move dist\main.exe Å×ÎïÏßÑİÊ¾Æ÷.exe
rd /s /q build
rd /s /q dist