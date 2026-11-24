import ast
from dataclasses import dataclass, asdict


@dataclass
class Finding:
    line: int
    kind: str
    explanation: str
    complexity: str


def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _bound_label(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Attribute):
        return node.attr
    return "n"


def analyze(source: str) -> dict:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {
            "time": "Unknown",
            "space": "Unknown",
            "confidence": "Low",
            "limitations": [f"Static syntax error: {exc.msg} at line {exc.lineno}"],
            "findings": [],
            "counts": {},
        }

    loops = []
    nested_count = 0
    recursion_calls = []
    allocations = []
    sorting = []
    function_calls = []

    class Visitor(ast.NodeVisitor):
        def visit_For(self, node):
            loops.append(node)
            self.generic_visit(node)

        visit_AsyncFor = visit_For

        def visit_While(self, node):
            loops.append(node)
            self.generic_visit(node)

        def visit_Call(self, node):
            name = _name(node.func)
            function_calls.append(node)
            if name in {"sort", "sorted"}:
                sorting.append(node)
            self.generic_visit(node)

        def visit_List(self, node):
            allocations.append(node)
            self.generic_visit(node)

        def visit_Dict(self, node):
            allocations.append(node)
            self.generic_visit(node)

        def visit_Set(self, node):
            allocations.append(node)
            self.generic_visit(node)

    Visitor().visit(tree)

    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            children = [
                child for child in ast.walk(node)
                if isinstance(child, (ast.For, ast.While)) and child is not node
            ]
            if children:
                nested_count += 1

    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    recursion_calls = [
        call for call in ast.walk(tree)
        if isinstance(call, ast.Call) and _name(call.func) in function_names
    ]

    loop_complexities = []
    findings = []
    for node in loops:
        if isinstance(node, ast.For):
            bound = "n"
            if isinstance(node.iter, ast.Call) and _name(node.iter.func) == "range":
                if node.iter.args:
                    bound = _bound_label(node.iter.args[-1])
            complexity = "O(n)"
            explanation = f"This loop executes across approximately {bound} iterations."
            kind = "loop"
        else:
            is_halving = any(
                isinstance(stmt, ast.AugAssign)
                and isinstance(stmt.op, (ast.FloorDiv, ast.LShift))
                for stmt in ast.walk(node)
            )
            is_doubling = any(
                isinstance(stmt, ast.AugAssign)
                and isinstance(stmt.op, (ast.Mult, ast.RShift))
                for stmt in ast.walk(node)
            )
            complexity = "O(log n)" if (is_halving or is_doubling) else "O(n)"
            explanation = "This loop appears to scale logarithmically." if complexity == "O(log n)" else "The while-loop bound could not be proven constant or logarithmic."
            kind = "loop"
        loop_complexities.append(complexity)
        findings.append(Finding(node.lineno, kind, explanation, complexity))

    fibonacci_style = any(
        isinstance(node, ast.BinOp)
        and isinstance(node.op, ast.Add)
        and sum(
            1 for call in ast.walk(node)
            if isinstance(call, ast.Call) and _name(call.func) in function_names
        ) >= 2
        for node in ast.walk(tree)
    )

    if nested_count:
        time = "O(n^2)" if nested_count == 1 else "O(n^3)" if nested_count == 2 else "O(n^k)"
    elif fibonacci_style:
        time = "O(2^n)"
    elif "O(log n)" in loop_complexities and len(loop_complexities) == 1:
        time = "O(log n)"
    elif loop_complexities:
        time = "O(n)" if len(set(loop_complexities)) == 1 else "O(n)"
    elif sorting:
        time = "O(n log n)"
    elif recursion_calls:
        time = "O(n)"
    else:
        time = "O(1)"

    if recursion_calls:
        space_aux = "O(n)"
    elif allocations:
        input_dependent = any(isinstance(call, ast.Call) and _name(call.func) in {"range", "zeros", "ones"} for call in ast.walk(tree))
        space_aux = "O(n)" if input_dependent or len(allocations) > 2 else "O(1)"
    else:
        space_aux = "O(1)"

    for node in sorting:
        findings.append(Finding(node.lineno, "sorting", "Sorting may add n log n work; this estimate depends on the method.", "O(n log n)"))
    for node in allocations:
        findings.append(Finding(node.lineno, "allocation", "This expression creates or allocates a data structure.", "O(n)"))
    for node in recursion_calls:
        findings.append(Finding(node.lineno, "recursion", "A recursive call was detected; account for call-stack memory.", "O(n)"))

    confidence = "Medium" if loops or recursion_calls or sorting else "High"
    return {
        "time": time,
        "space": space_aux,
        "confidence": confidence,
        "auxiliary_space": space_aux,
        "input_space": "O(n)",
        "output_space": "O(1)",
        "recursion_stack": "O(n)" if recursion_calls else "O(1)",
        "findings": [asdict(f) for f in findings],
        "counts": {
            "loops": len(loops),
            "nested_loops": nested_count,
            "recursive_calls": len(recursion_calls),
            "allocations": len(allocations),
            "function_calls": len(function_calls),
            "sorting_operations": len(sorting),
        },
        "limitations": ["This is a conservative rule-based estimate, not an exact proof of Big-O complexity."],
    }
