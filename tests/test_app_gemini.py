"""Tests for inline generate_content in app.py (mock mode)."""
import os

os.environ["SKIP_APP_FACTORY"] = "1"
os.environ.setdefault("LLM_MOCK", "1")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app import call_gemini_json, get_llm_mode
from llm.schemas import SemanticAnalysisResponse
from services.json_context import build_prompt


def test_get_llm_mode_mock():
    assert get_llm_mode() == "mock"


def test_call_gemini_json_mock_semantic():
    prompt = build_prompt(
        "3A_semantic_analysis",
        {
            "user_input": "Let's work together.",
            "active_agents": ["Commander"],
            "scenario_context_summary": "Deadline pressure.",
        },
        scenario_index=1,
    )
    result = call_gemini_json(
        "3A_semantic_analysis", prompt, SemanticAnalysisResponse
    )
    assert result.communication_signals.empathy > 0
    assert result.leadership_style_tag


def test_call_gemini_json_uses_generate_content_path(monkeypatch):
    called = {}

    class FakeResponse:
        text = '{"communication_signals":{"empathy":0.5,"clarity":0.5,"decisiveness":0.5,"aggression":0.1,"supportiveness":0.5,"adaptability":0.5},"leadership_style_tag":"Coaching","conflict_escalation_risk":"low"}'

    def fake_generate_content(self, **kwargs):
        called["model"] = kwargs.get("model")
        called["contents"] = kwargs.get("contents")
        return FakeResponse()

    class FakeModels:
        def generate_content(self, **kwargs):
            return fake_generate_content(None, **kwargs)

    class FakeClient:
        models = FakeModels()

    import app as app_module
    from config import Config

    os.environ["SKIP_APP_FACTORY"] = "1"
    monkeypatch.setattr(Config, "LLM_MOCK", False)
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(app_module, "_gemini_client", lambda: FakeClient())

    prompt = "test prompt"
    result = call_gemini_json(
        "3A_semantic_analysis", prompt, SemanticAnalysisResponse
    )
    assert result.leadership_style_tag == "Coaching"
    assert called["model"] is not None
    assert called["contents"] == prompt
