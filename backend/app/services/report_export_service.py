from html import escape
from io import BytesIO
from textwrap import wrap


def _safe_list(items) -> list:
    return items if isinstance(items, list) else []


def _section(title: str, lines: list[str]) -> list[str]:
    return [f"## {title}", "", *lines, ""]


def _bullets(items, empty_message: str) -> list[str]:
    values = [f"- {item}" for item in _safe_list(items)]

    return values or [empty_message]


def build_report_markdown(report) -> str:
    pylint_report = report.pylint_report or {}
    bandit_report = report.bandit_report or {}
    radon_report = report.radon_report or {}
    ai_review = report.ai_review or {}
    documentation_report = report.documentation_report or {}

    lines = [
        f"# AI Code Review Report - {report.filename}",
        "",
        f"- Report ID: {report.id}",
        f"- Created: {report.created_at}",
        f"- Pylint Score: {pylint_report.get('score', 'N/A')}/10",
        f"- Security Issues: {bandit_report.get('total_issues', 0)}",
        f"- Complexity Items: {len(_safe_list(radon_report.get('grades')))}",
        "",
    ]

    lines.extend(
        _section(
            "Pylint Findings",
            [
                f"- {issue.get('type', 'issue').upper()}: {issue.get('message', '')} "
                f"(Line {issue.get('line', 'N/A')})"
                for issue in _safe_list(pylint_report.get("issues"))
            ]
            or ["No Pylint findings."],
        )
    )

    lines.extend(
        _section(
            "Security Findings",
            [
                f"- {issue.get('issue_severity', 'INFO')}: {issue.get('issue_text', '')} "
                f"(Line {issue.get('line_number', 'N/A')})"
                for issue in _safe_list(bandit_report.get("issues"))
            ]
            or ["No security findings."],
        )
    )

    lines.extend(
        _section(
            "Complexity Analysis",
            [
                "```text",
                radon_report.get("complexity") or "No complexity details.",
                "```",
                "",
                "Maintainability:",
                "```text",
                radon_report.get("maintainability") or "N/A",
                "```",
            ],
        )
    )

    lines.extend(
        _section(
            "AI Review",
            [
                f"- Rating: {ai_review.get('overall_rating', 'N/A')}",
                f"- Summary: {ai_review.get('summary', 'N/A')}",
                "",
                "### Bugs",
                *_bullets(ai_review.get("bugs"), "No bugs reported."),
                "",
                "### Security Improvements",
                *_bullets(
                    ai_review.get("security_recommendations"),
                    "No security improvements reported.",
                ),
                "",
                "### Optimization",
                *_bullets(
                    ai_review.get("optimization_suggestions"),
                    "No optimization suggestions reported.",
                ),
                "",
                "### Better Naming",
                *_bullets(
                    ai_review.get("naming_suggestions"),
                    "No naming suggestions reported.",
                ),
                "",
                "### Refactoring",
                *_bullets(
                    ai_review.get("refactoring_suggestions"),
                    "No refactoring suggestions reported.",
                ),
                "",
                "### Performance",
                *_bullets(
                    ai_review.get("performance_recommendations"),
                    "No performance recommendations reported.",
                ),
                "",
                "### Best Practices",
                *_bullets(
                    ai_review.get("best_practices"),
                    "No best-practice suggestions reported.",
                ),
            ],
        )
    )

    lines.extend(
        _section(
            "Generated Documentation",
            [
                documentation_report.get("markdown")
                or documentation_report.get("summary")
                or "No documentation generated."
            ],
        )
    )

    return "\n".join(lines)


def build_report_html(report) -> str:
    markdown = build_report_markdown(report)
    escaped_markdown = escape(markdown)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AI Code Review Report - {escape(report.filename)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #111827; }}
    pre {{ background: #f3f4f6; border-radius: 8px; padding: 18px; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <pre>{escaped_markdown}</pre>
</body>
</html>
"""


def build_report_pdf(report) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    x = 50
    y = height - 50
    line_height = 13

    pdf.setTitle(f"AI Code Review Report - {report.filename}")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x, y, f"AI Code Review Report - {report.filename}")
    y -= 28
    pdf.setFont("Helvetica", 9)

    for raw_line in build_report_markdown(report).splitlines()[2:]:
        wrapped_lines = wrap(raw_line, width=95) or [""]

        for line in wrapped_lines:
            if y < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 9)
                y = height - 50

            pdf.drawString(x, y, line)
            y -= line_height

    pdf.save()
    buffer.seek(0)
    return buffer.read()
