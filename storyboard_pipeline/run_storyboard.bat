@echo off
setlocal
python "%~dp0generate_storyboard.py" %*
if errorlevel 1 exit /b %errorlevel%
echo.
echo Storyboard is ready in noir_film_project\output\NOIR_storyboard.html

