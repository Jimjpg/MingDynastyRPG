@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   大明王朝RPG - Windows 打包脚本
echo ========================================
echo.

echo [1/3] 检查 PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)
echo PyInstaller 已就绪
echo.

echo [2/3] 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "大明RPG.spec" del /q "大明RPG.spec"
echo 清理完成
echo.

echo [3/3] 开始打包...
pyinstaller --noconfirm --onefile --windowed ^
  --name "大明RPG" ^
  --icon "app.ico" ^
  --add-data "assets;assets" ^
  --add-data "map;map" ^
  --add-data "data;data" ^
  main.py

echo.
if exist "dist\大明RPG.exe" (
    echo ========================================
    echo   打包成功！
    echo   输出文件: dist\大明RPG.exe
    echo ========================================
) else (
    echo ========================================
    echo   打包失败，请检查上方错误信息
    echo ========================================
)
pause
