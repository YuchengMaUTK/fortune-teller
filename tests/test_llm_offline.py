import pytest

from fortune_teller.core.llm_connector import LLMConnector


@pytest.mark.parametrize("provider", ["openai", "deepseek", "anthropic", "aws_bedrock"])
def test_missing_client_reports_error_without_mock(monkeypatch, provider):
    monkeypatch.setattr(LLMConnector, "_initialize_client", lambda self: None)
    connector = LLMConnector({"provider": provider})
    text, metadata = connector.generate_response("system", "user")
    assert text.startswith("Error:")
    assert "error" in metadata
    assert not connector.cache
    assert "not initialized" in "".join(connector.generate_response_streaming("system", "user"))


def test_unknown_provider_reports_error():
    connector = LLMConnector({"provider": "typo"})
    assert "Unsupported" in connector.generate_response("s", "u")[0]
    assert "Unsupported" in "".join(connector.generate_response_streaming("s", "u"))


def test_explicit_mock_is_labeled():
    connector = LLMConnector({"provider": "mock"})
    text, metadata = connector.generate_response("s", "u")
    assert text.startswith("[MOCK]")
    assert metadata["mock"] is True
    assert "".join(connector.generate_response_streaming("s", "u")).startswith("[MOCK]")


def test_initialization_exception_is_handled(monkeypatch):
    def fail(self):
        raise ValueError("missing API key")
    monkeypatch.setattr(LLMConnector, "_initialize_client", fail)
    connector = LLMConnector({"provider": "anthropic"})
    assert "error" in connector.generate_response("s", "u")[1]
    assert connector.set_provider("anthropic") is False


def test_failed_response_is_not_cached(monkeypatch):
    monkeypatch.setattr(LLMConnector, "_initialize_client", lambda self: None)
    connector = LLMConnector({"provider": "openai"})
    connector.client = object()
    responses = iter([("Error: timeout", {"error": "timeout"}), ("real response", {})])
    monkeypatch.setattr(connector, "_call_openai", lambda *args: next(responses))
    assert "error" in connector.generate_response("s", "u")[1]
    assert connector.generate_response("s", "u")[0] == "real response"


def test_prompts_not_logged_at_info(monkeypatch, caplog):
    monkeypatch.setattr(LLMConnector, "_initialize_client", lambda self: None)
    connector = LLMConnector({"provider": "openai"})
    with caplog.at_level("INFO"):
        connector.generate_response("private system prompt", "private birthday")
        list(connector.generate_response_streaming("private system prompt", "private birthday"))
    assert "private birthday" not in caplog.text
    assert "private system prompt" not in caplog.text
