import json

from openai import OpenAI

from app.config import settings


def _empty_ai_review(status: str, message: str) -> dict:
    return {
        "status": status,
        "overall_rating": "Not available",
        "summary": message,
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
        ai_review["status"] = "completed"

        return ai_review

    except Exception as exc:
        return _empty_ai_review(
            "failed",
            f"AI review failed: {str(exc)}",
        )
