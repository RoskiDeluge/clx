"""
Thin task-style helpers that wrap `clx_query`.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Optional, Tuple

from .core import Cache, clx_query


def clx_gen(
    model: str,
    prompt: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    backend_url: Optional[str] = None,
    cache: Optional[Cache] = None,
    expect_json: bool = False,
    timeout: Optional[Tuple[int, int]] = None,
) -> Any:
    return clx_query(
        model=model,
        prompt=prompt,
        params=params,
        backend_url=backend_url,
        cache=cache,
        expect_json=expect_json,
        timeout=timeout or (5, 30),
    )


def clx_summarize(
    model: str,
    text: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:
    prompt = f"Summarize this:\n{text}"
    return clx_gen(model, prompt, params=params, **kwargs)


def clx_translate(
    model: str,
    text: str,
    target_lang: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:
    prompt = f"Translate the following text to {target_lang}:\n{text}"
    return clx_gen(model, prompt, params=params, **kwargs)


def clx_classify(
    model: str,
    text: str,
    labels: Iterable[str],
    *,
    params: Optional[Dict[str, Any]] = None,
    expect_json: bool = True,
    **kwargs: Any,
) -> Any:
    label_list = ", ".join(labels)
    prompt = (
        "Classify the following text into one of the provided labels. "
        "Return only the label.\n"
        f"Labels: {label_list}\n"
        f"Text: {text}"
    )
    return clx_gen(model, prompt, params=params, expect_json=expect_json, **kwargs)


def clx_extract(
    model: str,
    text: str,
    schema: Any,
    *,
    params: Optional[Dict[str, Any]] = None,
    expect_json: bool = True,
    **kwargs: Any,
) -> Any:
    schema_repr = json.dumps(schema, indent=2, ensure_ascii=False)
    prompt = (
        "Extract structured data from the following text according to the provided JSON schema. "
        "Respond with valid JSON only.\n"
        f"Schema:\n{schema_repr}\n\n"
        f"Text:\n{text}"
    )
    return clx_gen(model, prompt, params=params, expect_json=expect_json, **kwargs)


def clx_similarity(
    model: str,
    a: str,
    b: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    expect_json: bool = True,
    **kwargs: Any,
) -> Any:
    prompt = (
        "Compare the following two inputs and return a similarity score between 0 and 1 "
        "along with a short justification as JSON.\n"
        f"Input A:\n{a}\n\nInput B:\n{b}"
    )
    return clx_gen(model, prompt, params=params, expect_json=expect_json, **kwargs)


def clx_fix_grammar(
    model: str,
    text: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Any:
    prompt = f"Fix grammar and spelling in the following text while preserving meaning:\n{text}"
    return clx_gen(model, prompt, params=params, **kwargs)
