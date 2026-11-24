from app.execution import execute_python


def test_imports_installed_package_from_runtime_environment():
    result = execute_python("import pytest\nprint(pytest.__version__)")
    assert result["status"] == "success"
    assert result["stdout"].strip()
