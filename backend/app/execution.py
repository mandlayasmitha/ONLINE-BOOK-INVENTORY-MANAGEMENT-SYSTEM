import os
import json
import importlib.util
import subprocess
import sys
import tempfile
import time


def execute_python(source: str, stdin: str = "", timeout_ms: int = 3000) -> dict:
    python = sys.executable
    package_paths = [
        path for path in sys.path
        if os.path.isabs(path)
        and os.path.isdir(path)
        and os.path.basename(path).lower() in {"site-packages", "dist-packages"}
    ]
    for package in ("numpy", "pandas", "requests", "sympy"):
        spec = importlib.util.find_spec(package)
        if spec and spec.submodule_search_locations:
            package_paths.extend(
                os.path.dirname(location)
                for location in spec.submodule_search_locations
                if os.path.isdir(location)
            )
        elif spec and spec.origin:
            package_paths.append(os.path.dirname(spec.origin))
    package_paths = list(dict.fromkeys(package_paths))

    with tempfile.TemporaryDirectory(prefix="cca-") as directory:
        path = os.path.join(directory, "main.py")
        with open(path, "w", encoding="utf-8") as file:
            file.write(source)
        started = time.perf_counter()
        try:
            result = subprocess.run(
                [
                    python,
                    "-I",
                    "-B",
                    "-c",
                    "import json, os, runpy, sys; "
                    "sys.path.extend(json.loads(os.environ['CCA_SITE_PACKAGES'])); "
                    "runpy.run_path(sys.argv[1], run_name='__main__')",
                    path,
                ],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout_ms / 1000,
                cwd=directory,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONIOENCODING": "utf-8",
                    "CCA_SITE_PACKAGES": json.dumps(package_paths),
                },
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
