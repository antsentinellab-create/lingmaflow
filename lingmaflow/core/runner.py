"""Safe Process Runner - Industrial grade subprocess wrapper.

Handles OOM prevention, zombie process reaping, and encoding safety.
"""
import subprocess
import tempfile
from typing import List, Tuple


class SafeProcessRunner:
    """Executes external commands with strict resource limits."""

    @staticmethod
    def run(
        cmd: List[str], 
        timeout: int = 300, 
        max_output_kb: int = 10
    ) -> Tuple[bool, str]:
        """Run a command safely and return (success, output).
        
        Args:
            cmd: Command list (e.g., ['behave', 'path'])
            timeout: Seconds before killing the process
            max_output_kb: Max KB of output to capture (prevents OOM)
            
        Returns:
            Tuple of (is_success, captured_output)
        """
        max_bytes = max_output_kb * 1024
        
        try:
            # Physical isolation: Write to disk instead of RAM
            with tempfile.TemporaryFile(mode='w+', encoding='utf-8', errors='replace') as out_f, \
                 tempfile.TemporaryFile(mode='w+', encoding='utf-8', errors='replace') as err_f:
                
                process = subprocess.Popen(
                    cmd,
                    stdout=out_f,
                    stderr=err_f,
                    text=True,
                    errors='replace'  # Prevent UnicodeDecodeError
                )
                
                try:
                    process.wait(timeout=timeout)
                    success = (process.returncode == 0)
                    
                    # Read limited content for reporting
                    out_f.seek(0)
                    err_f.seek(0)
                    output = err_f.read(max_bytes) if not success else out_f.read(max_bytes)
                    
                    # Truncate indicator
                    if len(output) >= max_bytes:
                        output += "\n... [Output truncated due to length]"
                        
                    return success, output
                    
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()  # Reap zombie process
                    return False, f"⏱️ Execution timed out after {timeout}s"
                    
        except FileNotFoundError:
            return False, f"⚠️ Command not found: {cmd[0]}"
        except Exception as e:
            return False, f"💥 Unexpected error: {type(e).__name__}: {str(e)}"
