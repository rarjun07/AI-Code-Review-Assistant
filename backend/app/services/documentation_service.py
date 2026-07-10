import ast


def _format_arguments(node: ast.FunctionDef) -> list[str]:
    arguments = []

    for argument in node.args.args:
        if argument.arg != "self":
            arguments.append(argument.arg)

    return arguments


def _function_summary(node: ast.FunctionDef) -> dict:
    docstring = ast.get_docstring(node)
    arguments = _format_arguments(node)

    return {
        "name": node.name,
        "line_number": node.lineno,
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
    }

    documentation["markdown"] = _build_markdown(documentation)

    return documentation
