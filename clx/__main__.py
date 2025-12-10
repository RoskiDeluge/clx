"""
Entrypoint shim for `python -m clx`.
"""

from __future__ import annotations

from . import clx_query


def main() -> None:
    message = (
        "clx is now a minimal AI resolver library. "
        "Import and call `clx.clx_query` instead of using the CLI."
    )
    try:
        # Tiny sanity check to ensure the import worked.
        _ = clx_query  # noqa: F841
    finally:
        print(message)


if __name__ == "__main__":
    main()
