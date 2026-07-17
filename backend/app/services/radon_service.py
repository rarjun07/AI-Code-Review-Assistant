import subprocess
import re


def run_radon(file_path: str):
    # Cyclomatic Complexity
    cc_result = subprocess.run(
        ["radon", "cc", file_path, "-s"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Maintainability Index
    mi_result = subprocess.run(
        ["radon", "mi", file_path],
        capture_output=True,
        text=True,
        timeout=30,
    )

    complexity_output = cc_result.stdout
    maintainability_output = mi_result.stdout

    grades = re.findall(r"\((.)\)", complexity_output)

    return {
        "complexity": complexity_output,
        "maintainability": maintainability_output,
        "grades": grades,
    }
