import json

from openai import AuthenticationError, OpenAI, RateLimitError

from app.config import settings


def _empty_ai_review(
    status: str,
    message: str,
    provider: str = "none",
) -> dict:
    return {
        "status": status,
        "provider": provider,
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
        "optimization_suggestions": [],
        "performance_recommendations": [],
        "naming_suggestions": [],
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
  "optimization_suggestions": ["optimization suggestion"],
  "performance_recommendations": ["performance recommendation"],
  "naming_suggestions": ["better naming suggestion"],
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
    list_fields = [
        "strengths",
        "bugs",
        "security_recommendations",
        "optimization_suggestions",
        "performance_recommendations",
        "naming_suggestions",
        "refactoring_suggestions",
        "best_practices",
    ]

    for field in list_fields:
        if not isinstance(ai_review.get(field), list):
            ai_review[field] = []

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


def _get_provider_configuration() -> dict | None:
    if settings.AI_PROVIDER in {"auto", "huggingface"} and settings.HF_TOKEN:
        return {
            "name": "huggingface",
            "label": "Hugging Face",
            "api_key": settings.HF_TOKEN,
            "model": settings.HUGGINGFACE_MODEL,
            "base_url": settings.HUGGINGFACE_BASE_URL,
        }

    if settings.AI_PROVIDER in {"auto", "openai"} and settings.OPENAI_API_KEY:
        return {
            "name": "openai",
            "label": "OpenAI",
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL,
            "base_url": None,
        }

    return None


def generate_ai_review(
    code: str,
    pylint_report: dict,
    bandit_report: dict,
    radon_report: dict,
) -> dict:
    provider = _get_provider_configuration()

    if provider is None:
        requested_provider = settings.AI_PROVIDER.title()

        return _empty_ai_review(
            "skipped",
            f"{requested_provider} AI credentials are not configured. "
            "Add HF_TOKEN (recommended) or OPENAI_API_KEY to backend/.env.",
        )

    try:
        client_options = {"api_key": provider["api_key"]}

        if provider["base_url"]:
            client_options["base_url"] = provider["base_url"]

        client = OpenAI(**client_options)

        response = client.chat.completions.create(
            model=provider["model"],
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
        ai_review["provider"] = provider["name"]

        return ai_review

    except AuthenticationError:
        return _empty_ai_review(
            "failed",
            f"{provider['label']} credentials are invalid. Update the token "
            "in backend/.env and restart the backend.",
            provider["name"],
        )

    except RateLimitError:
        return _empty_ai_review(
            "failed",
            f"{provider['label']} quota is not available. Check the account's "
            "credits and usage limits, then try again.",
            provider["name"],
        )

    except Exception as exc:
        return _empty_ai_review(
            "failed",
            f"{provider['label']} AI review failed: {str(exc)}",
            provider["name"],
        )
