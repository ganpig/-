@echo off
pipenv run pyinstaller main.spec
move dist\main.exe ��������ʾ��.exe
rd /s /q build
rd /s /q dist