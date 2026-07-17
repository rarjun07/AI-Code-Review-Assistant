import ast


def _format_arguments(node: ast.FunctionDef) -> list[str]:
    arguments = []

    for argument in node.args.args:
        if argument.arg != "self":
            arguments.append(argument.arg)

    return arguments


def _node_line_count(node: ast.AST) -> int:
    end_line = getattr(node, "end_lineno", None)
    start_line = getattr(node, "lineno", None)

    if not end_line or not start_line:
        return 0

    return end_line - start_line + 1


def _function_summary(node: ast.FunctionDef) -> dict:
    docstring = ast.get_docstring(node)
    arguments = _format_arguments(node)

    return {
        "name": node.name,
        "line_number": node.lineno,
        "line_count": _node_line_count(node),
        "arguments": arguments,
        "docstring": docstring or "No docstring available.",
        "summary": (
            f"Function `{node.name}` accepts {len(arguments)} argument(s)."
        ),
    }


def _class_summary(node: ast.ClassDef) -> dict:
    methods = [
        _function_summary(child)
        for child in node.body
        if isinstance(child, ast.FunctionDef)
    ]

    return {
        "name": node.name,
        "line_number": node.lineno,
        "docstring": ast.get_docstring(node) or "No docstring available.",
        "methods": methods,
        "method_count": len(methods),
    }


def _build_markdown(documentation: dict) -> str:
    lines = [
        f"# Documentation for {documentation['filename']}",
        "",
        "## Module Summary",
        documentation["module_docstring"],
        "",
        "## Functions",
    ]

    if documentation["functions"]:
        for function in documentation["functions"]:
            arguments = ", ".join(function["arguments"]) or "No arguments"
            lines.extend(
                [
                    f"### {function['name']}",
                    f"- Line: {function['line_number']}",
                    f"- Arguments: {arguments}",
                    f"- Summary: {function['summary']}",
                    f"- Docstring: {function['docstring']}",
                    "",
                ]
            )
    else:
        lines.extend(["No top-level functions found.", ""])

    lines.append("## Classes")

    if documentation["classes"]:
        for class_item in documentation["classes"]:
            lines.extend(
                [
                    f"### {class_item['name']}",
                    f"- Line: {class_item['line_number']}",
                    f"- Methods: {class_item['method_count']}",
                    f"- Docstring: {class_item['docstring']}",
                    "",
                ]
            )
    else:
        lines.extend(["No classes found.", ""])

    return "\n".join(lines)


def _code_metrics(code: str, tree: ast.AST) -> dict:
    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    classes = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]
    function_lengths = [
        _node_line_count(node)
        for node in functions
        if _node_line_count(node) > 0
    ]

    average_function_length = (
        round(sum(function_lengths) / len(function_lengths), 2)
        if function_lengths
        else 0
    )

    return {
        "number_of_classes": len(classes),
        "number_of_functions": len(functions),
        "total_lines_of_code": len(code.splitlines()),
        "average_function_length": average_function_length,
    }


def generate_documentation(code: str, filename: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "status": "failed",
            "filename": filename,
            "summary": "Documentation could not be generated because the uploaded file has a syntax error.",
            "error": str(exc),
            "module_docstring": "Not available.",
            "functions": [],
            "classes": [],
            "metrics": {
                "number_of_classes": 0,
                "number_of_functions": 0,
                "total_lines_of_code": len(code.splitlines()),
                "average_function_length": 0,
            },
            "markdown": "",
        }

    functions = [
        _function_summary(node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    ]

    classes = [
        _class_summary(node)
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    ]

    documentation = {
        "status": "completed",
        "filename": filename,
        "summary": (
            f"Generated documentation for {len(functions)} function(s) "
            f"and {len(classes)} class(es)."
        ),
        "module_docstring": ast.get_docstring(tree)
        or "No module docstring available.",
        "functions": functions,
        "classes": classes,
        "metrics": _code_metrics(code, tree),
    }

    documentation["markdown"] = _build_markdown(documentation)

    return documentation
