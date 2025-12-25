@echo off
REM Simple stop script - Kill all Python processes on FastAPI ports
echo Stopping FastAPI servers on ports 8008, 8009, 8010...

REM Kill processes on specific ports
netstat -ano | findstr ":8008 " | for /f "tokens=5" %%a in ('more') do taskkill /f /pid %%a 2>nul
netstat -ano | findstr ":8009 " | for /f "tokens=5" %%a in ('more') do taskkill /f /pid %%a 2>nul  
netstat -ano | findstr ":8010 " | for /f "tokens=5" %%a in ('more') do taskkill /f /pid %%a 2>nul

echo Done. All servers on ports 8008-8010 have been stopped.
timeout /t 3