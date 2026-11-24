from app.execution import execute_python


def test_imports_installed_package_from_runtime_environment():
    result = execute_python(
        "import numpy as np\nimport pandas as pd\n"
        "print(np.array([2, 4]).sum())\nprint(pd.__version__)",
        timeout_ms=10000,
    )
    assert result["status"] == "success"
    assert result["stdout"].splitlines()[0] == "6"
