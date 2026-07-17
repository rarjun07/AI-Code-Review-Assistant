import json
import re
import subprocess


def run_pylint(file_path: str):
    # -------------------------
    # Run 1: JSON report
    # -------------------------
    json_result = subprocess.run(
        [
            "pylint",
            file_path,
            "--output-format=json",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    try:
        issues = json.loads(json_result.stdout)
    except json.JSONDecodeError:
        issues = []

    # -------------------------
    # Run 2: Text report
    # -------------------------
    text_result = subprocess.run(
        [
            "pylint",
            file_path,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    score = None

    match = re.search(
        r"rated at\s+([-\d\.]+)/10",
        text_result.stdout,
    )

    if match:
        score = match.group(1)

    return {
        "issues": issues,
        "score": score,
        "raw_output": json_result.stdout,
    }
