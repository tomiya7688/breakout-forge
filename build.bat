@echo off
setlocal
cd /d "%~dp0"

set "DIST_DIR=dist\BreakoutForge"

echo [1/4] Cleaning previous build output...
if exist build rmdir /s /q build
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"

echo [2/4] Building BreakoutForge with PyInstaller onedir...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
  --windowed ^
  --name BreakoutForge ^
  --contents-directory _internal ^
  --paths src ^
  src\breakout_forge\__main__.py
if errorlevel 1 exit /b %errorlevel%

echo [3/4] Copying editable external data beside the executable...
python scripts\prepare_dist.py --project-root . --dist-root "%DIST_DIR%"
if errorlevel 1 exit /b %errorlevel%

echo [4/4] Running packaged smoke test...
"%DIST_DIR%\BreakoutForge.exe" --smoke-test
if errorlevel 1 exit /b %errorlevel%

echo.
echo Build succeeded: %DIST_DIR%
exit /b 0
