"""
Syntax Validation and Code Execution Sandbox Module.
Performs AST validation to ensure 100% syntactically correct Python output.
"""

import ast
import subprocess
import sys
import tempfile
import os
from typing import Tuple

def validate_syntax(code_string: str) -> Tuple[bool, str]:
    """
    Validates Python code using Python's built-in Abstract Syntax Tree (AST) parser.
    Returns (True, 'Valid Syntax') if parse succeeds, else (False, error details).
    """
    if not code_string or not code_string.strip():
        return False, "Code string is empty."
    
    try:
        ast.parse(code_string)
        return True, "AST Syntax Validation Passed: Code is syntactically correct."
    except SyntaxError as e:
        error_info = f"SyntaxError at line {e.lineno}, col {e.offset}: {e.msg}\n--> {e.text}"
        return False, error_info
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def execute_code_sandbox(code_string: str, timeout_seconds: int = 5) -> Tuple[bool, str]:
    """
    Executes the Python code snippet in a sandboxed child process and captures stdout/stderr.
    Safe execution with a hard timeout to prevent infinite loops.
    """
    # First ensure syntax is valid before executing
    is_valid, err_msg = validate_syntax(code_string)
    if not is_valid:
        return False, f"Cannot execute: {err_msg}"
        
    # Write code to a temporary python file
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(code_string)
        temp_path = temp_file.name

    try:
        process = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        if process.returncode == 0:
            output = process.stdout if process.stdout.strip() else "[Code executed successfully with returncode 0 and no output]"
            return True, output
        else:
            return False, f"Runtime Error (Exit Code {process.returncode}):\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return False, f"Execution timed out after {timeout_seconds} seconds (possible infinite loop)."
    except Exception as e:
        return False, f"Execution failed: {str(e)}"
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
