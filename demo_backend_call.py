"""
Standalone runner to exercise clx_query against a configured backend.

Usage:
    python3 demo_backend_call.py "What is 2+2?" --model my-backend-model
    python3 demo_backend_call.py "What is 2+2?" --metadata '{"user_id": "user_123"}'

Configuration is pulled from environment variables (or a local .env file):
    CLX_BACKEND_URL   Base URL, e.g. https://your-worker.workers.dev
    CLX_POD_NAME      Pod identifier (for pod/actor routes)
    CLX_ACTOR_ID      Actor identifier (for pod/actor routes)
    CLX_METADATA      Optional JSON metadata string, e.g. '{"user_id":"user_123"}'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict

from clx import Cache, clx_query


def load_env_file(path: str = ".env") -> None:
    """Minimal .env loader to avoid extra dependencies."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def parse_metadata(raw: str | None) -> Dict[str, object]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Metadata must be valid JSON")
    if not isinstance(parsed, dict):
        raise ValueError("Metadata must be a JSON object")
    return parsed


def main() -> None:
    load_env_file()

    parser = argparse.ArgumentParser(description="Demo call to clx_query.")
    parser.add_argument("prompt", help="Prompt to send to the backend.")
    parser.add_argument(
        "--model",
        help="Backend model name (overrides CLX_MODEL, defaults to 'demo-model').",
        default=None,
    )
    parser.add_argument(
        "-m",
        "--metadata",
        help="Optional JSON metadata payload (overrides CLX_METADATA).",
        default=None,
    )
    args = parser.parse_args()

    prompt = args.prompt

    backend_url = os.environ.get("CLX_BACKEND_URL")
    pod_name = os.environ.get("CLX_POD_NAME")
    actor_id = os.environ.get("CLX_ACTOR_ID")
    model = args.model or os.environ.get("CLX_MODEL") or "demo-model"
    metadata = {}
    cli_metadata = args.metadata
    env_metadata = os.environ.get("CLX_METADATA")

    try:
        if cli_metadata is not None:
            metadata = parse_metadata(cli_metadata)
        elif env_metadata:
            metadata = parse_metadata(env_metadata)
    except ValueError as exc:
        print(f"Invalid metadata: {exc}")
        sys.exit(1)

    if not backend_url:
        print("Missing CLX_BACKEND_URL. Set it in your environment or .env file.")
        sys.exit(1)

    if not (pod_name and actor_id):
        print("Missing CLX_POD_NAME or CLX_ACTOR_ID. Set them in your environment or .env file.")
        sys.exit(1)

    try:
        with Cache(enabled=False) as cache:
            result = clx_query(
                model=model,
                prompt=prompt,
                backend_url=backend_url,
                pod_name=pod_name,
                actor_id=actor_id,
                metadata=metadata,
                use_messages_payload=True,
                cache=cache,
            )
    except Exception as exc:  # noqa: BLE001
        print(f"Request failed: {exc}")
        sys.exit(1)

    print("\n--- Response ---")
    print(result)


if __name__ == "__main__":
    main()
