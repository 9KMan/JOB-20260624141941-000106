python
// src/core/bedrock.py
"""AWS Bedrock LLM client.

Thin wrapper around ``boto3`` that uses the Bedrock ``converse`` API
(unified across model providers) so we can swap models via configuration
without changing call sites.
"""
from __future__ import annotations

import json
import os
from typing import Any

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError


class BedrockError(RuntimeError):
    """Raised when an AWS Bedrock invocation fails."""


class BedrockClient:
    """Synchronous client for AWS Bedrock Runtime.

    Credentials are sourced from the standard boto3 chain (environment
    variables, shared config, IAM role) — no secrets are hardcoded.
    """

    def __init__(
        self,
        region: str | None = None,
        model_id: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.4,
    ) -> None:
        self.region = region or os.environ.get("AWS_REGION", "us-east-1")
        self.model_id = model_id or os.environ.get(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-sonnet-20240229-v1:0",
        )
        self.max_tokens = max_tokens
        self.temperature = temperature

        boto_config = BotoConfig(
            region_name=self.region,
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=10,
            read_timeout=120,
        )
        self.client = boto3.client("bedrock-runtime", config=boto_config)

    def invoke(self, prompt: str, system: str = "") -> str:
        """Send a single user-turn message to the configured model.

        Args:
            prompt: The user-role message body.
            system: Optional system prompt.

        Returns:
            The model's text response.

        Raises:
            BedrockError: If the Bedrock call fails for any reason.
        """
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        kwargs: dict[str, Any] = {
            "modelId": self.model_id,
            "messages": messages,
            "inferenceConfig": {
                "maxTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }
        if system:
            kwargs["system"] = [{"text": system}]

        try:
            response = self.client.converse(**kwargs)
        except (ClientError, BotoCoreError) as exc:
            raise BedrockError(f"Bedrock invocation failed: {exc}") from exc

        try:
            content_blocks = response["output"]["message"]["content"]
            text_segments = [
                block["text"] for block in content_blocks if "text" in block
            ]
            return "".join(text_segments)
        except (KeyError, TypeError) as exc:
            raise BedrockError(f"Unexpected Bedrock response shape: {json.dumps(response)[:500]}") from exc

