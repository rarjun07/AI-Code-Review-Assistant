import json
import subprocess


def run_bandit(file_path: str):
    result = subprocess.run(
        [
            "bandit",
            "-f",
            "json",
            file_path,
        ],
        capture_output=True,
        text=True,
    )

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {
            "results": [],
            "metrics": {},
        }

    issues = report.get("results", [])
    metrics = report.get("metrics", {})

    high_severity = sum(
        1 for issue in issues
        if issue.get("issue_severity") == "HIGH"
    )

    medium_severity = sum(
        1 for issue in issues
        if issue.get("issue_severity") == "MEDIUM"
    )

    low_severity = sum(
        1 for issue in issues
        if issue.get("issue_severity") == "LOW"
    )

    return {
        "issues": issues,
        "metrics": metrics,
        "high_severity": high_severity,
        "medium_severity": medium_severity,
        "low_severity": low_severity,
        "total_issues": len(issues),
    }