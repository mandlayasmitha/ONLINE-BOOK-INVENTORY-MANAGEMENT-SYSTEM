import os
import shutil
import subprocess
import tempfile
import time


def execute_python(source: str, stdin: str = "", timeout_ms: int = 3000) -> dict:
    python = shutil.which("python") or shutil.which("python3")
    if not python:
        return {"status": "error", "stdout": "", "stderr": "Python runtime is unavailable.", "exitCode": None, "executionTimeMs": 0, "memoryMb": None, "security": "Development adapter"}

    with tempfile.TemporaryDirectory(prefix="cca-") as directory:
        path = os.path.join(directory, "main.py")
        with open(path, "w", encoding="utf-8") as file:
            file.write(source)
        started = time.perf_counter()
        try:
            result = subprocess.run(
                [python, "-I", "-B", path],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout_ms / 1000,
                cwd=directory,
                env={"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"},
            )
            elapsed = round((time.perf_counter() - started) * 1000, 2)
            return {
                "status": "success" if result.returncode == 0 else "runtime_error",
                "stdout": result.stdout[-100_000:],
                "stderr": result.stderr[-100_000:],
                "exitCode": result.returncode,
                "executionTimeMs": elapsed,
                "memoryMb": None,
                "security": "WARNING: development-only subprocess; not Docker isolated",
            }
        except subprocess.TimeoutExpired:
            elapsed = round((time.perf_counter() - started) * 1000, 2)
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": f"Execution exceeded {timeout_ms} ms.",
                "exitCode": None,
                "executionTimeMs": elapsed,
                "memoryMb": None,
                "security": "WARNING: development-only subprocess; not Docker isolated",
            }
