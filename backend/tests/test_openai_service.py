import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.openai_service import generate_ai_review


class OpenAIReviewServiceTests(unittest.TestCase):
    def test_review_is_skipped_when_api_key_is_missing(self):
        with (
            patch("app.services.openai_service.settings.AI_PROVIDER", "auto"),
            patch("app.services.openai_service.settings.HF_TOKEN", None),
            patch("app.services.openai_service.settings.OPENAI_API_KEY", None),
        ):
            review = generate_ai_review("print('hello')\n", {}, {}, {})

        self.assertEqual(review["status"], "skipped")
        self.assertEqual(review["findings"], [])
        self.assertIn("not configured", review["summary"])

    @patch("app.services.openai_service.OpenAI")
    def test_successful_review_is_normalized(self, openai_client):
        model_review = {
            "overall_rating": "Good",
            "summary": "The function is clear and small.",
            "findings": [
                {
                    "severity": "medium",
                    "category": "Best Practice",
                    "title": "Add type hints",
                    "description": "The parameters have no type hints.",
                    "suggestion": "Annotate both parameters and the return value.",
                },
                {
                    "severity": "unexpected value",
                    "title": "Add a docstring",
                },
            ],
            "strengths": ["Simple implementation"],
        }
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(model_review))
                )
            ]
        )
        openai_client.return_value.chat.completions.create.return_value = response

        with (
            patch("app.services.openai_service.settings.AI_PROVIDER", "openai"),
            patch(
                "app.services.openai_service.settings.OPENAI_API_KEY",
                "test-key",
            ),
        ):
            review = generate_ai_review(
                "def add(a, b):\n    return a + b\n",
                {"score": 10},
                {"results": []},
                {"complexity": 1},
            )

        self.assertEqual(review["status"], "completed")
        self.assertEqual(review["provider"], "openai")
        self.assertEqual(review["overall_rating"], "Good")
        self.assertEqual(review["severity_summary"]["medium"], 1)
        self.assertEqual(review["severity_summary"]["info"], 1)
        self.assertEqual(review["findings"][0]["severity"], "Medium")
        self.assertEqual(review["findings"][1]["severity"], "Info")
        self.assertEqual(review["bugs"], [])
        openai_client.assert_called_once_with(api_key="test-key")

    @patch("app.services.openai_service.OpenAI")
    def test_auto_provider_prefers_hugging_face(self, openai_client):
        response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=json.dumps(
                            {
                                "overall_rating": "Good",
                                "summary": "Review completed.",
                                "findings": [],
                            }
                        )
                    )
                )
            ]
        )
        openai_client.return_value.chat.completions.create.return_value = response

        with (
            patch("app.services.openai_service.settings.AI_PROVIDER", "auto"),
            patch("app.services.openai_service.settings.HF_TOKEN", "hf_test"),
            patch(
                "app.services.openai_service.settings.OPENAI_API_KEY",
                "openai-test-key",
            ),
            patch(
                "app.services.openai_service.settings.HUGGINGFACE_MODEL",
                "Qwen/test-model:cheapest",
            ),
        ):
            review = generate_ai_review("print('hello')\n", {}, {}, {})

        self.assertEqual(review["status"], "completed")
        self.assertEqual(review["provider"], "huggingface")
        openai_client.assert_called_once_with(
            api_key="hf_test",
            base_url="https://router.huggingface.co/v1",
        )
        call = openai_client.return_value.chat.completions.create.call_args
        self.assertEqual(call.kwargs["model"], "Qwen/test-model:cheapest")

    @patch("app.services.openai_service.OpenAI")
    def test_unexpected_provider_error_returns_failed_review(self, openai_client):
        openai_client.return_value.chat.completions.create.side_effect = RuntimeError(
            "provider unavailable"
        )

        with (
            patch("app.services.openai_service.settings.AI_PROVIDER", "openai"),
            patch(
                "app.services.openai_service.settings.OPENAI_API_KEY",
                "test-key",
            ),
        ):
            review = generate_ai_review("print('hello')\n", {}, {}, {})

        self.assertEqual(review["status"], "failed")
        self.assertEqual(review["findings"], [])
        self.assertIn("provider unavailable", review["summary"])


if __name__ == "__main__":
    unittest.main()
