"""
Core primitives for the minimal clx resolver.

This module exposes `clx_query`, along with lightweight config and caching
helpers. All model traffic is forwarded to a user-supplied backend that
implements the `/v1/query` contract.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import requests

try:  # Python <3.11 fallback
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

DEFAULT_CONFIG_PATH = Path("~/.clx/config.toml").expanduser()
DEFAULT_CACHE_PATH = Path("~/.clx_cache.db").expanduser()
DEFAULT_BACKEND_PATH = "/v1/query"


@dataclass
class Config:
    backend_url: str


class Cache:
    """
    Optional SQLite-backed cache keyed by backend URL, model, prompt, params, and routing.

    Disabled unless explicitly passed into `clx_query`.
    """

    def __init__(self, path: Union[str, Path] = DEFAULT_CACHE_PATH, enabled: bool = True):
        self.path = Path(path).expanduser()
        self.enabled = enabled
        self._conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> "Cache":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def _connect(self) -> sqlite3.Connection:
        if not self.enabled:
            raise RuntimeError("Cache is disabled")

        if self._conn is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.path)
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        return self._conn

    @staticmethod
    def build_key(
        backend_url: str,
        backend_path: str,
        model: str,
        prompt: str,
        params: Dict[str, Any],
        metadata: Optional[Dict[str, Any]],
        use_messages_payload: bool,
    ) -> str:
        canonical = json.dumps(
            {
                "backend_url": backend_url,
                "backend_path": backend_path,
                "model": model,
                "prompt": prompt,
                "params": params,
                "metadata": metadata or {},
                "use_messages_payload": use_messages_payload,
            },
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def get(self, cache_key: str) -> Optional[Any]:
        if not self.enabled:
            return None

        conn = self._connect()
        row = conn.execute("SELECT value FROM cache WHERE cache_key = ?", (cache_key,)).fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except Exception:
            return row[0]

    def set(self, cache_key: str, value: Any) -> None:
        if not self.enabled:
            return

        conn = self._connect()
        try:
            serialized = json.dumps(value)
        except TypeError:
            serialized = json.dumps(str(value))

        conn.execute(
            "INSERT OR REPLACE INTO cache (cache_key, value) VALUES (?, ?)",
            (cache_key, serialized),
        )
        conn.commit()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.commit()
            self._conn.close()
            self._conn = None


def load_config(path: Union[str, Path] = DEFAULT_CONFIG_PATH) -> Optional[Config]:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return None

    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    backend_url = data.get("backend_url") or data.get("backend", {}).get("url")
    if not backend_url:
        return None

    return Config(backend_url=str(backend_url))


def resolve_backend_url(
    backend_url: Optional[str] = None, *, config_path: Union[str, Path] = DEFAULT_CONFIG_PATH
) -> str:
    if backend_url:
        return backend_url.rstrip("/")

    env_backend = os.environ.get("CLX_BACKEND_URL")
    if env_backend:
        return env_backend.rstrip("/")

    config = load_config(config_path)
    if config and config.backend_url:
        return config.backend_url.rstrip("/")

    raise ValueError(
        "No backend URL provided. "
        "Set CLX_BACKEND_URL, add backend_url to ~/.clx/config.toml, "
        "or pass backend_url directly to clx_query()."
    )


def resolve_backend_path(
    backend_path: Optional[str] = None,
    *,
    pod_name: Optional[str] = None,
    actor_id: Optional[str] = None,
) -> str:
    """
    Build a backend path. Defaults to /v1/query, or if pod/actor is provided,
    uses /pods/{pod}/actors/{actor}/run.
    """
    if backend_path:
        return backend_path

    pod = pod_name or os.environ.get("CLX_POD_NAME")
    actor = actor_id or os.environ.get("CLX_ACTOR_ID")
    if pod and actor:
        return f"/pods/{pod}/actors/{actor}/run"

    return DEFAULT_BACKEND_PATH


def _ensure_json_payload(output: Any) -> Any:
    if isinstance(output, (dict, list)):
        return output
    if isinstance(output, str):
        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:  # pragma: no cover - passthrough raising
            raise ValueError("Backend output was not valid JSON") from exc
    raise ValueError(f"Unsupported JSON output type: {type(output).__name__}")


def clx_query(
    model: str,
    prompt: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    backend_url: Optional[str] = None,
    backend_path: Optional[str] = None,
    pod_name: Optional[str] = None,
    actor_id: Optional[str] = None,
    cache: Optional[Cache] = None,
    metadata: Optional[Dict[str, Any]] = None,
    expect_json: bool = False,
    use_messages_payload: bool = False,
    timeout: Tuple[int, int] = (5, 30),
) -> Any:
    """
    Forward a query to the configured backend.

    Args:
        model: Model identifier expected by the backend.
        prompt: Prompt text to send.
        params: Optional model parameters forwarded verbatim.
        backend_url: Override backend URL. Falls back to env/config.
        backend_path: Optional path suffix. Defaults to /v1/query, or to
            /pods/{pod}/actors/{actor}/run if pod/actor is provided.
            If set to a full URL, it is used directly.
        pod_name: Optional pod name used when building the path.
        actor_id: Optional actor id used when building the path.
        cache: Optional Cache instance. If provided, enables caching.
        metadata: Optional metadata payload for backends that support it.
        expect_json: If True, attempts to parse the backend output as JSON.
        use_messages_payload: If True, send payload as {"messages": [...]} rather than
            {"model": ..., "prompt": ...}.
        timeout: (connect_timeout, read_timeout) tuple passed to requests.
    """
    resolved_backend = resolve_backend_url(backend_url)
    resolved_path = resolve_backend_path(backend_path, pod_name=pod_name, actor_id=actor_id)
    params = params or {}
    meta = metadata or {}
    cache_key = None

    if cache:
        cache_key = cache.build_key(
            resolved_backend,
            resolved_path,
            model,
            prompt,
            params,
            meta,
            use_messages_payload,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached if not expect_json else _ensure_json_payload(cached)

    if use_messages_payload:
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "metadata": meta,
        }
        # preserve model/params if the backend wants to branch on them
        if model:
            payload["model"] = model
        if params:
            payload["params"] = params
    else:
        payload = {"model": model, "prompt": prompt, "params": params, "metadata": meta or None}

    if resolved_path.startswith("http://") or resolved_path.startswith("https://"):
        endpoint = resolved_path
    else:
        endpoint = f"{resolved_backend}/{resolved_path.lstrip('/')}"

    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to reach backend at {endpoint}") from exc

    if response.status_code >= 400:
        raise RuntimeError(f"Backend returned {response.status_code}: {response.text}")

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("Backend response was not valid JSON") from exc

    # Try the standard contract first
    if "output" in data:
        output = data["output"]
    elif "response" in data:
        output = data["response"]
    else:
        raise ValueError("Backend response missing 'output' or 'response' field")

    if expect_json:
        output = _ensure_json_payload(output)

    if cache and cache_key:
        cache.set(cache_key, output)

    return output
