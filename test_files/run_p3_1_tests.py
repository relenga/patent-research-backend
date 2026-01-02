"""
P3.1 Database Test Execution Script

Executes P3.1 database functional tests in compliance with AgentRules.md 
Command Length Rule (<120 chars). All test execution commands are contained
in this script to avoid terminal command length violations.
"""
import sys
import os
import subprocess


def run_p31_database_tests():
    """Execute P3.1 database functional tests with proper configuration."""
    python_exe = r"C:/Users/AiDev/Documents/RevelHMIPatentCode-v2/.venv/Scripts/python.exe"
    cmd = [
        python_exe, "-m", "pytest",
        "test_files/test_p3_1_database.py",
        "-v", "--tb=short"
    ]
    
    result = subprocess.run(cmd, cwd=r"C:\Users\AiDev\Documents\RevelHMIPatentCode-v2")
    return result.returncode


def run_schema_creation_tests():
    """Execute only schema creation tests."""
    python_exe = r"C:/Users/AiDev/Documents/RevelHMIPatentCode-v2/.venv/Scripts/python.exe"
    cmd = [
        python_exe, "-m", "pytest",
        "test_files/test_p3_1_database.py::TestP31DatabaseSchema",
        "-v"
    ]
    
    result = subprocess.run(cmd, cwd=r"C:\Users\AiDev\Documents\RevelHMIPatentCode-v2")
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "schema":
        exit_code = run_schema_creation_tests()
    else:
        exit_code = run_p31_database_tests()
    
    sys.exit(exit_code)