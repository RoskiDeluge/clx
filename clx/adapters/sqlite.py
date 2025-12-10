"""
SQLite SQL integration.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from ..core import Cache, clx_query


def register_clx_query(
    connection: Any,
    *,
    backend_url: Optional[str] = None,
    cache: Optional[Cache] = None,
    expect_json: bool = False,
) -> None:
    """
    Register `clx_query` as a SQLite SQL function.

    Example:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        register_clx_query_sqlite(conn)
    """

    def _clx_query_fn(model: str, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        output = clx_query(
            model=model,
            prompt=prompt,
            params=params or {},
            backend_url=backend_url,
            cache=cache,
            expect_json=expect_json,
        )
        return json.dumps(output) if expect_json else str(output)

    connection.create_function("clx_query", 3, _clx_query_fn)
