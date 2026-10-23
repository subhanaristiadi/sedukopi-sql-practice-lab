@echo off
setlocal
cd /d "%~dp0"
echo ==================================================
echo Publish Sedukopi SQL Practice Lab to GitHub
echo ==================================================
where git >nul 2>nul
if errorlevel 1 (
  echo ERROR: Git is not installed or not on PATH.
  echo Install Git for Windows, reopen this window, and run this file again.
  pause
  exit /b 1
)
if exist .git (
  echo ERROR: This folder already contains a .git directory.
  echo Stop here to avoid overwriting an existing repository setup.
  pause
  exit /b 1
)
set /p REPO_URL=Paste the URL of the EMPTY GitHub repository ending in .git: 
if "%REPO_URL%"=="" (
  echo No repository URL supplied.
  pause
  exit /b 1
)
echo.
echo This will commit the files in this folder and push them to:
echo %REPO_URL%
echo .gitignore excludes .env, CSV files, ZIP files, and local artifacts.
set /p CONFIRM=Continue? Type YES to confirm: 
if /I not "%CONFIRM%"=="YES" (
  echo Cancelled. No repository changes were made.
  pause
  exit /b 0
)
git init -b main
if errorlevel 1 goto failed
git add .
if errorlevel 1 goto failed
git status --short
echo.
set /p COMMIT_OK=Review the file list above. Type YES to commit and push: 
if /I not "%COMMIT_OK%"=="YES" (
  echo Cancelled before commit. Removing the temporary local .git folder; no push occurred.
  rmdir /s /q .git
  pause
  exit /b 0
)
git commit -m "Initial Sedukopi SQL Practice Lab cloud deployment"
if errorlevel 1 goto failed
git remote add origin "%REPO_URL%"
if errorlevel 1 goto failed
git push -u origin main
if errorlevel 1 goto failed
echo.
echo Successfully pushed main to GitHub.
pause
exit /b 0
:failed
echo.
echo An operation failed. Read the Git message above; no secrets should be shared in chat.
pause
exit /b 1
