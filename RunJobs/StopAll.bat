@echo off
REM Stop all running servers for this FastAPI project
echo Stopping all FastAPI servers...

REM Kill all uvicorn processes (FastAPI server)
echo Stopping uvicorn processes...
taskkill /f /im "uvicorn.exe" 2>nul
if errorlevel 1 (
    echo No uvicorn processes found.
) else (
    echo Stopped uvicorn processes.
)

REM Kill all Python processes running uvicorn module
echo Stopping Python processes running uvicorn...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr "uvicorn"') do (
    taskkill /f /pid %%i 2>nul
    if not errorlevel 1 echo Stopped Python process %%i
)

REM Kill processes using common FastAPI ports
echo Checking for processes using ports 8008, 8009, 8010...
for %%p in (8008 8009 8010) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p "') do (
        taskkill /f /pid %%a 2>nul
        if not errorlevel 1 echo Stopped process using port %%p (PID: %%a)
    )
)

echo.
echo All FastAPI servers have been stopped.
pause