import json
import re
import subprocess  # nosec B404
import sys
from pathlib import Path


def _run_pylint(source: str, source_name: str, output_format: str | None = None):
    command = [
        sys.executable,
        "-m",
        "pylint",
        "--from-stdin",
        source_name,
    ]

    if output_format:
        command.append(f"--output-format={output_format}")

    return subprocess.run(  # nosec B603
        command,
        input=source,
        capture_output=True,
        text=True,
        timeout=30,
    )


def run_pylint(file_path: str, source_name: str | None = None):
    source = Path(file_path).read_text(encoding="utf-8", errors="replace")
    analyzed_name = source_name or Path(file_path).name

    # -------------------------
    # Run 1: JSON report
    # -------------------------
    json_result = _run_pylint(source, analyzed_name, "json")

    try:
        issues = json.loads(json_result.stdout)
    except json.JSONDecodeError:
        issues = []

    # -------------------------
    # Run 2: Text report
    # -------------------------
    text_result = _run_pylint(source, analyzed_name)

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
