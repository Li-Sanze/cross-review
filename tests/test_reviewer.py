"""Tests for reviewer backend resolution and standalone Anthropic backend."""

from __future__ import annotations

import builtins
import sys
from types import SimpleNamespace

import pytest

from crossreview.reviewer import (
    AnthropicReviewerBackend,
    ReviewerConfigurationError,
    ReviewerDependencyError,
    UnsupportedReviewerProviderError,
    resolve_reviewer_backend,
)
from crossreview.schema import FileMeta, ReviewPack, ReviewerConfig


def _pack() -> ReviewPack:
    return ReviewPack(
        diff="diff --git a/a.py b/a.py\n@@ -1 +1 @@\n-print('a')\n+print('b')\n",
        changed_files=[FileMeta(path="a.py", language="python")],
        artifact_fingerprint="artifact",
        pack_fingerprint="pack",
        intent="fix output",
    )


class TestReviewerBackendResolution:
    def test_resolve_anthropic_backend(self):
        backend = resolve_reviewer_backend(
            ReviewerConfig(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                api_key_env="ANTHROPIC_API_KEY",
            )
        )
        assert isinstance(backend, AnthropicReviewerBackend)

    def test_unsupported_provider_raises(self):
        with pytest.raises(UnsupportedReviewerProviderError):
            resolve_reviewer_backend(
                ReviewerConfig(
                    provider="openai",
                    model="gpt-4o",
                    api_key_env="OPENAI_API_KEY",
                )
            )


class TestAnthropicReviewerBackend:
    def test_missing_api_key_env_raises(self):
        backend = AnthropicReviewerBackend()
        with pytest.raises(ReviewerConfigurationError):
            backend.review(
                _pack(),
                ReviewerConfig(
                    provider="anthropic",
                    model="claude-sonnet-4-20250514",
                    api_key_env="ANTHROPIC_API_KEY",
                ),
            )

    def test_missing_dependency_raises(self, monkeypatch):
        backend = AnthropicReviewerBackend()
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        original_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "anthropic":
                raise ImportError("missing anthropic")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        with pytest.raises(ReviewerDependencyError):
            backend.review(
                _pack(),
                ReviewerConfig(
                    provider="anthropic",
                    model="claude-sonnet-4-20250514",
                    api_key_env="ANTHROPIC_API_KEY",
                ),
            )

    def test_success_path_with_fake_sdk(self, monkeypatch):
        backend = AnthropicReviewerBackend()
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        class FakeMessages:
            def create(self, **_kwargs):
                return SimpleNamespace(
                    content=[SimpleNamespace(type="text", text="## Section 1: Findings\n\nNo findings.")],
                    usage=SimpleNamespace(input_tokens=123, output_tokens=45),
                )

        class FakeAnthropicClient:
            def __init__(self, *, api_key: str):
                self.api_key = api_key
                self.messages = FakeMessages()

        monkeypatch.setitem(sys.modules, "anthropic", SimpleNamespace(Anthropic=FakeAnthropicClient))

        response = backend.review(
            _pack(),
            ReviewerConfig(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                api_key_env="ANTHROPIC_API_KEY",
            ),
        )

        assert response.model == "claude-sonnet-4-20250514"
        assert "No findings" in response.raw_analysis
        assert response.input_tokens == 123
        assert response.output_tokens == 45
