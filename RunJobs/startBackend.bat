@echo off
REM Phase 0 / Phase 1 startup
REM Assumes venv already created and synced

call .venv\Scripts\activate

REM Use uv as dev tool (declared in dev deps)
uv run uvicorn src.app.main:app --reload
