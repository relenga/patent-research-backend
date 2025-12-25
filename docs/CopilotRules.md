# Copilot Project Rules (Authoritative)

These rules are non-negotiable and apply to all Copilot assistance
(code, debugging, prompts, and suggestions).

**See also:** [AgentRules.md](AgentRules.md) for global agent governance and phase control rules.

## Execution Environment Rules

**These rules apply to ALL Copilot assistance: Project Manager, Debugging, Development, Architecture, and Testing chats.**

1. **Copilot MUST NOT start backend or frontend servers.**
   - Do not use VS Code integrated terminals.
   - Do not suggest `npm start`, `npm run dev`, `uvicorn`, or similar
     commands as actions.
   - Commands may be provided for reference only.

2. **Copilot MUST NOT activate virtual environments via VS Code terminals**
   - Do not run `Activate.ps1` or similar activation scripts in VS Code terminals
   - Do not use VS Code terminal-based environment activation
   - These operations cause terminal hangs and backend startup failures

3. **All servers are started using Windows native terminals only**
   via batch files in the `RunJobs/` directory:
   - `RunJobs/StartBackEnd.bat`
   - `RunJobs/StartBoth.bat`

4. Backend crashes that occur only in VS Code integrated terminals
   are considered **environment artifacts**, not code defects.

5. Copilot must not propose code changes whose sole purpose is to
   mitigate VS Code terminal crashes.

**VIOLATION CONSEQUENCES**: VS Code terminal operations by Copilot cause:
- Stuck activation processes consuming resources
- Backend startup failures (Exit Code: 1 patterns)
- Terminal hangs requiring manual termination
- Environment corruption affecting all subsequent operations

## Terminal Command Execution Rules (CRITICAL)

**These rules prevent the 40% command failure rate in Windows PowerShell environment.**

### PowerShell Command Syntax (MANDATORY)
1. **Use semicolon (;) instead of && for command chaining**
   - ✅ CORRECT: `cd "path" ; command`
   - ❌ INCORRECT: `cd "path" && command` (causes "not a valid statement separator" error)

2. **Use PowerShell-native commands instead of Linux equivalents**
   - ✅ CORRECT: `Select-String -Pattern "text"`
   - ❌ INCORRECT: `grep -E "text"` (command not recognized)
   - ✅ CORRECT: `Get-Content file.txt`
   - ❌ INCORRECT: `cat file.txt`

### Python Command Execution (MANDATORY)
3. **Always specify full virtual environment paths**
   - ✅ CORRECT: `.\venv\Scripts\python.exe`
   - ❌ INCORRECT: `python` (environment context loss)

4. **Create .py files for complex Python commands**
   - ✅ CORRECT: Create temp script for f-string operations
   - ❌ INCORRECT: Inline f-strings in PowerShell (escaping failures)

### Command Execution Strategy (MANDATORY)
5. **Prefer VS Code tasks over raw terminal commands**
   - Use `run_task` tool when available tasks exist
   - Check task definitions before creating new terminal commands

6. **Validate environment before package operations**
   - Test virtual environment activation
   - Verify package availability before import commands

7. **Split long commands into multiple steps**
   - Avoid command truncation issues
   - Improve error isolation and debugging

8. **Command Length Limits (NEW - CRITICAL)**
   - ✅ CORRECT: Create .py files for commands longer than 120 characters (REDUCED LIMIT)
   - ❌ INCORRECT: Inline commands that get truncated in terminal
   - ✅ CORRECT: Create .py files for complex paths or multiple arguments
   - All created .py files MUST go in `test_files/` directory
   - Use descriptive filenames: `test_retry_document.py`, `check_gpu_status.py`

## Inter-Chat Communication Rules (MANDATORY)

**These rules apply when creating prompts for other specialized chats (Debugging, Development, Architecture, Testing).**

### Prompt Format Requirements
1. **NO CODE BLOCKS in inter-chat prompts**
   - ✅ CORRECT: Describe code locations and requirements in plain text
   - ❌ INCORRECT: Include ```code``` blocks that don't copy/paste properly
   - ✅ CORRECT: "Fix the function in backend/routers/corpus.py line 45-60"
   - ❌ INCORRECT: Including actual code snippets in prompt

2. **Copy/Paste Safe Formatting**
   - Use only plain text, bullet points, and markdown formatting
   - Avoid any content that won't transfer in copy/paste operations
   - Test that prompts are complete when copied and pasted

3. **Complete Context in Text Form**
   - Describe file locations, line numbers, and requirements clearly
   - Include all necessary context without relying on code blocks
   - Use descriptive text instead of code examples

**VIOLATION IMPACT:** Code blocks in prompts create incomplete instructions when copied, wasting time and causing confusion in specialized chats.

### Test File Placement
1. **All temporary/testing .py files MUST be created in `test_files/` directory**
   - ✅ CORRECT: `test_files/retry_document.py`
   - ❌ INCORRECT: `retry_doc.py` in project root

2. **File Naming Convention for Test Files**
   - Use descriptive names: `test_[functionality].py`
   - Examples: `test_hitl_workflow.py`, `check_pipeline_status.py`

3. **Clean Project Structure**
   - Project root should only contain: main config files, directories, README
   - Keep temporary scripts in designated `test_files/` location

## Debugging Scope Rules

- Focus only on deterministic, code-level defects.
- If an issue cannot be reproduced outside VS Code terminals,
  Copilot must explicitly conclude: "No code-level defect identified."

## Database Session Management Standards (MANDATORY)

**⚠️ ARCHITECTURAL AUTHORITY:** Database session patterns are managed by Architecture chat only. Do not modify without consultation.

### Required Database Pattern
1. **Import Standard:**
   - ✅ CORRECT: `from backend.core.database import get_session`
   - ❌ INCORRECT: `from backend.core.database import db_manager`
   - ❌ INCORRECT: Direct Session/engine imports

2. **Usage Pattern:**
   - ✅ CORRECT: `with get_session() as session:`
   - ❌ INCORRECT: `with db_manager.get_session() as session:`
   - ❌ INCORRECT: Manual session creation

3. **Transaction Handling:**
   - Context manager provides automatic commit/rollback
   - No manual transaction management required
   - Session cleanup guaranteed

### Development Standards
1. **All New Database Code:** Must use approved get_session() pattern
2. **Router Development:** Must validate database access uses consistent patterns
3. **Service Classes:** Must use centralized session management
4. **Error Debugging:** Must reference approved patterns for database access issues

This section is binding for all Development, Debugging, and Architecture assistance.

## API Endpoint Standards - Mandatory Trailing Slash Consistency

**CRITICAL: These standards prevent recurring 404 errors between FastAPI backend and frontend clients.**

### Backend Router Rules (MANDATORY)

1. **FastAPI Router Definitions:**
   - All base routes MUST use consistent trailing slash patterns
   - @router.get("/") creates endpoints requiring trailing slashes
   - Example: @router.get("/") in tasks router creates /api/tasks/ endpoint

2. **Path Registration Standards:**
   - Root endpoints: @router.get("/") → /api/resource/
   - Sub-endpoints: @router.get("/detail") → /api/resource/detail
   - List endpoints: @router.get("/list") → /api/resource/list

### Frontend API Client Rules (MANDATORY)

1. **Endpoint Path Matching:**
   - Frontend calls MUST match exact backend endpoint paths
   - Include trailing slashes where backend requires them
   - Example: Backend /api/tasks/ requires frontend call to "/api/tasks/"

2. **Correct vs Incorrect Patterns:**
   - ✅ CORRECT: fetch("/api/tasks/") matches @router.get("/")
   - ❌ INCORRECT: fetch("/api/tasks") causes 404 with @router.get("/")
   - ✅ CORRECT: fetch("/api/tasks/detail") matches @router.get("/detail")

### Development Standards

1. **All New Endpoints:** Must follow established trailing slash patterns
2. **API Client Development:** Must validate paths match backend exactly  
3. **Debugging Sessions:** Must reference these standards for 404 issues
4. **Code Reviews:** Must verify endpoint path consistency

### Common Problem Resolution

**Issue:** 404 errors on API calls despite backend running
**Check:** Trailing slash consistency between backend router and frontend calls
**Solution:** Match exact paths including trailing slashes

## Database Session Management Standards (CRITICAL)

**ARCHITECTURE AUTHORITY: This standardization is binding for ALL development work.**

### Approved Database Session Pattern (MANDATORY)

**✅ CORRECT PATTERN:**
```python
from backend.core.database import get_session

# Usage in all routers and services:
with get_session() as session:
    # database operations here
    result = session.query(Model).all()
```

**❌ DEPRECATED PATTERNS (FORBIDDEN):**
- `from backend.core.database import db_manager` + `db_manager.get_session()`
- Direct Session creation with `create_engine`
- Manual session management without context manager
- Any direct `db_manager` imports or usage

### Implementation Requirements

1. **All Router Files**: Must use approved `get_session()` pattern
2. **All Service Files**: Must use approved `get_session()` pattern  
3. **Automatic Transaction Handling**: Context manager provides commit/rollback
4. **Session Cleanup**: Automatic resource cleanup via context manager

### Validation Criteria
- No "No parsed result found" errors
- All API endpoints functional
- Proper transaction handling confirmed
- No manual session creation code

**VIOLATION CONSEQUENCES**: Using deprecated patterns causes API failures and system instability.

This section is binding for all Development, Debugging, and Architecture assistance.

Failure to follow these rules is considered an incorrect response.
