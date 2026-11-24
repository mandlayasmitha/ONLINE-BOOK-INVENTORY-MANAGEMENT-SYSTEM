from app.static_analyzer import analyze


def test_constant():
    result = analyze("x = arr[0]\nprint(x)")
    assert result["time"] == "O(1)"


def test_linear_loop():
    result = analyze("n = 10\nfor i in range(n):\n    print(i)")
    assert result["time"] == "O(n)"


def test_nested_loop():
    result = analyze("for i in range(n):\n    for j in range(n):\n        print(i, j)")
    assert result["time"] == "O(n^2)"


def test_log_loop():
    result = analyze("i = 1\nwhile i < n:\n    i *= 2")
    assert result["time"] == "O(log n)"


def test_fibonacci():
    source = "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)"
    result = analyze(source)
    assert result["time"] == "O(2^n)"
