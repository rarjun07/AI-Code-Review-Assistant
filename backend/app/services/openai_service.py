import json

from openai import AuthenticationError, OpenAI, RateLimitError

from app.config import settings


def _empty_ai_review(status: str, message: str) -> dict:
    return {
        "status": status,
        "overall_rating": "Not available",
        "summary": message,
        "severity_summary": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        },
        "findings": [],
        "strengths": [],
        "bugs": [],
        "security_recommendations": [],
        "performance_recommendations": [],
        "refactoring_suggestions": [],
        "best_practices": [],
    }


def _build_prompt(
    code: str,
    pylint_report: dict,
    bandit_report: dict,
    radon_report: dict,
) -> str:
    return f"""
Review this Python source code as a senior software engineer.

Use the source code and the static-analysis reports from Pylint,
Bandit, and Radon. Focus on bugs, security issues, performance,
refactoring, naming, and best practices.

Return only valid JSON using this exact structure:

{{
  "overall_rating": "Excellent, Good, Needs Improvement, or Poor",
  "summary": "Short overall review",
  "severity_summary": {{
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  }},
  "findings": [
    {{
      "severity": "Critical, High, Medium, Low, or Info",
      "category": "Bug, Security, Performance, Refactoring, Best Practice, or Documentation",
      "title": "Short finding title",
      "description": "What is wrong or what can improve",
      "suggestion": "Specific fix or recommendation"
    }}
  ],
  "strengths": ["strength 1", "strength 2"],
  "bugs": ["bug or possible issue"],
  "security_recommendations": ["security recommendation"],
  "performance_recommendations": ["performance recommendation"],
  "refactoring_suggestions": ["refactoring suggestion"],
  "best_practices": ["best-practice suggestion"]
}}

Python code:
```python
{code}
```

Pylint report:
{json.dumps(pylint_report, indent=2)}

Bandit report:
{json.dumps(bandit_report, indent=2)}

Radon report:
{json.dumps(radon_report, indent=2)}
"""


def _normalize_ai_review(ai_review: dict) -> dict:
    findings = ai_review.get("findings")

    if not isinstance(findings, list):
        findings = []

    severity_summary = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
    }

    normalized_findings = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue

        severity = str(finding.get("severity", "Info")).strip().lower()

        if severity not in severity_summary:
            severity = "info"

        severity_summary[severity] += 1

        normalized_findings.append(
            {
                "severity": severity.title(),
                "category": finding.get("category", "General"),
                "title": finding.get("title", "Code review finding"),
                "description": finding.get("description", ""),
                "suggestion": finding.get("suggestion", ""),
            }
        )

    ai_review["findings"] = normalized_findings
    ai_review["severity_summary"] = severity_summary

    return ai_review


def generate_ai_review(
    code: str,
    pylint_report: dict,
    bandit_report: dict,
    radon_report: dict,
) -> dict:
    if not settings.OPENAI_API_KEY:
        return _empty_ai_review(
            "skipped",
            "OpenAI API key is not configured. "
            "Add OPENAI_API_KEY to backend/.env to enable AI review.",
        )

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You return concise, valid JSON for Python code reviews.",
                },
                {
                    "role": "user",
                    "content": _build_prompt(
                        code,
                        pylint_report,
                        bandit_report,
                        radon_report,
                    ),
                },
            ],
        )

        content = response.choices[0].message.content or "{}"
        ai_review = json.loads(content)
        ai_review = _normalize_ai_review(ai_review)
        ai_review["status"] = "completed"

        return ai_review

    except AuthenticationError:
        return _empty_ai_review(
            "failed",
            "OpenAI API key is invalid. Update OPENAI_API_KEY in backend/.env and restart the backend.",
        )

    except RateLimitError:
        return _empty_ai_review(
            "failed",
            "OpenAI API quota is not available. Check your OpenAI plan, billing, and usage limits, then try again.",
        )

    except Exception as exc:
        return _empty_ai_review(
            "failed",
            f"AI review failed: {str(exc)}",
        )
