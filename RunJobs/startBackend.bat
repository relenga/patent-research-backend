@echo off
REM Phase 1 startup - Start FastAPI server
REM Assumes venv already created and synced

echo.
echo ================================================================
echo REVEL HMI BACKEND STARTUP (Phase 1)
echo ================================================================
echo.
echo WARNING: This is the ONLY supported backend startup mechanism
echo Do NOT run uvicorn directly or use other startup methods
echo.

REM Change to project root directory
cd /d "%~dp0\.."

REM Activate virtual environment
call .venv\Scripts\activate

REM Start the FastAPI server with specific host and port
echo.
echo ================================================================
echo Starting FastAPI server...
echo.
echo Server will be available at:
echo   - Main API: http://127.0.0.1:8008/api/v1/
echo   - Documentation: http://127.0.0.1:8008/docs
echo   - Health Check: http://127.0.0.1:8008/api/v1/health
echo   - OpenAPI Schema: http://127.0.0.1:8008/openapi.json
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

uv run uvicorn src.app.main:app --host 127.0.0.1 --port 8008 --reload

echo.
echo ================================================================
echo SERVER STOPPED
echo ================================================================
echo.
echo The FastAPI server has stopped running.
echo If this was unexpected, check the error messages above.
echo.
pause
