clx — Minimal AI Resolver Library
Refactor Specification - part 1

This document outlines the initial architecture and scope for the refactored clx project. The goal is to provide a minimal, backend-agnostic AI resolver that can be used in any Python environment and exposed as SQL functions across engines such as Spark, DuckDB, SQLite, and more. The user supplies their own backend endpoint that hosts foundation models.

1. Core primitive: clx_query

clx_query(model, prompt, params) is the only required operation in clx.

Sends all requests to a user-provided backend via HTTP.

Returns either a string or JSON.

Handles optional caching and JSON validation.

All “task helpers” (summarize, classify, extract, etc.) are simple wrappers around clx_query.

clx does not talk directly to OpenAI/Ollama/Databricks models—only the user’s backend.

Example:

from clx.core import clx_query

result = clx_query(
    model="meta-llama-3-3-70b-instruct",
    prompt="Summarize this: " + text,
    params={"max_tokens": 120, "temperature": 0.3},
)

2. Backend configuration

clx requires the user to specify a backend URL. Precedence:

Function argument backend_url=...

Environment variable CLX_BACKEND_URL

(Optional) Config file at ~/.clx/config.toml

If no backend is provided, clx raises a clear error.

Example:

export CLX_BACKEND_URL="https://my-ai-backend.company.com"


Backend must expose an endpoint like:

POST /v1/query
{
  "model": "...",
  "prompt": "...",
  "params": { ... }
}


and return:

{ "output": ... }

3. Optional caching

clx ships with a lightweight SQLite-based cache:

Cache("~/.clx_cache.db")


Keyed by hash of backend URL + model + prompt + params.

Disabled by default.

Helps save cost/latency when prompts repeat (including Spark workloads).

4. Task helpers (thin wrappers)

clx includes optional convenience functions that wrap clx_query:

clx_gen(model, prompt, **params)

clx_summarize(model, text, **params)

clx_translate(model, text, target_lang, **params)

clx_classify(model, text, labels, **params)

clx_extract(model, text, schema, **params)

clx_similarity(model, a, b, **params)

clx_fix_grammar(model, text, **params)

These produce domain-specific prompts and forward all calls to clx_query.

Example:

from clx.tasks import clx_summarize
clx_summarize("meta-llama3", text, max_tokens=100)

5. Spark SQL integration (clx_query UDF)

clx provides an adapter to register clx_query as a Spark SQL function:

from clx.adapters.spark import register_clx_query
register_clx_query(spark)


Example SQL usage (Databricks-style):

df_out = df.selectExpr(
    "clx_query("
    "  'meta-llama-3-3-70b-instruct', "
    "  CONCAT('Please summarize: ', text), "
    "  named_struct('max_tokens', 100, 'temperature', 0.7)"
    ") AS summary"
)


Additional task-style UDFs (e.g., clx_summarize()) may be registered optionally.

6. DuckDB SQL integration

clx registers a function similar to Spark:

SELECT clx_query(
    'meta-llama3',
    'Summarize: ' || text,
    '{"max_tokens": 120}'
)
FROM docs;


Implementation uses con.create_function("clx_query", ...) and internally calls clx_query().

7. SQLite SQL integration

clx exposes clx_query as a SQLite function through conn.create_function.

Example:

SELECT clx_query('meta-llama3', 'Translate to French: ' || text, NULL)
FROM messages;


This makes clx extremely portable for lightweight analytics and local experimentation.

8. Minimal v1 feature set

The first release of clx should include:

Core

clx_query() (HTTP → backend)

Config resolution (backend_url + env var)

Optional caching

Error handling + timeouts

Tasks

clx_gen, clx_summarize, clx_translate, clx_classify

A few more simple helpers as desired

Adapters

Spark: register_clx_query(spark)

DuckDB: register_clx_query(con)

SQLite: register_clx_query_sqlite(conn)

Documentation

Python examples

Spark SQL example (your preferred selectExpr pattern)

DuckDB / SQLite examples

Backend API contract

This gives you a clean, minimal, extensible AI resolver that works anywhere, using your own backend.
