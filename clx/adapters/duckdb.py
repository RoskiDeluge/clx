"""
DuckDB SQL integration.
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
    Register `clx_query` as a DuckDB SQL function.

    Example:
        import duckdb
        con = duckdb.connect()
        register_clx_query(con)
    """

    def _clx_query_udf(model: str, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        output = clx_query(
            model=model,
            prompt=prompt,
            params=params or {},
            backend_url=backend_url,
            cache=cache,
            expect_json=expect_json,
        )
        return json.dumps(output) if expect_json else str(output)

    connection.create_function("clx_query", _clx_query_udf)
