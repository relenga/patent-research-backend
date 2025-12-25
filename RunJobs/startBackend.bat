@echo off
REM Phase 1 startup - Start FastAPI server
REM Assumes venv already created and synced

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
