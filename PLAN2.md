clx — Minimal AI Resolver Library
Refactor Specification - part 2

Right now Databricks is treating “observation/evaluation” as an add-on, mostly via things like query profiles, system tables, and separate Mosaic Agent Evaluation notebooks. You’re basically saying: I want that part to be first-class in my own backend, while clx stays tiny and generic on the client side. That’s a nice split of concerns.

Here’s how I’d shape things, comparing to Databricks and then tilting it toward your “eval-first” backend.

1. Keep clx ultra-thin, push all intelligence to the backend

Databricks has:

Many task-specific SQL functions (ai_summarize, ai_classify, etc.) 
Microsoft Learn

One general ai_query that routes to foundation models, external models, and custom endpoints. 
Microsoft Learn

You’re already on the right track with:

clx_query(model, prompt, params) as the only primitive.

Optional helpers like clx_summarize() that are just prompt templates.

So in clx-land:

clx = thin shim + function registration

No model selection logic.

No routing logic.

No evaluation logic.

Backend = brain

Decides which model to hit.

Handles logging, eval, guardrails, costs, experiments, etc.

That separation is exactly what gives you room to treat evaluation as first-class.

2. Make “observation” a first-class concept in the HTTP contract

Concretely, extend the backend API so every call from clx carries structured metadata about the “observation,” not just model/prompt/params.

Request shape

Something like:

{
  "model": "databricks-meta-llama-3-3-70b-instruct",
  "prompt": "Summarize the following text: ...",
  "params": { "max_tokens": 100, "temperature": 0.7 },
  "context": {
    "source": "spark_sql",                // or "pandas", "duckdb", "cli"
    "function": "clx_query",             // or "clx_summarize"
    "dataset": "catalog.schema.table",   // if available
    "run_id": "uuid-...",                // clx-generated or provided
    "user_id": "analyst_123",            // optional
    "tags": ["batch", "inference", "prod"],
    "trace_id": "trace-uuid-...",
    "eval_policy": "default"             // see below
  }
}


clx can auto-fill some of this (e.g., source, function, a random run_id) and expose knobs so users can add more.

Backend behavior

Every request = observation record:

request metadata (context, prompt, params)

model + version

raw response

timing, tokens, cost (if you have that)

eval results (can be initial empty, then filled in asynchronously)

That means the backend is not just “/v1/query,” it’s:

“/v1/query” + a data model around observations, evals, and runs.

3. Make evaluation pluggable at the backend level

Instead of baking eval into clx, put it behind backend policies.

Eval policies

Let context.eval_policy pick an evaluation pipeline:

"none" – no evaluation, just log.

"default" – cheap heuristics + maybe a small LLM/regex.

"golden_set:v1" – compare to ground truth in a reference table.

"llm_judge:v2" – use a judging model to score correctness / style / safety.

Your backend then:

Stores observations immediately.

Runs eval pipelines async or sync depending on policy & budget.

Writes eval results back into the same store, keyed by observation_id.

Types of evals

Structural: did the model return valid JSON / correct shape?

Task-specific:

For classification: label accuracy vs. ground truth.

For extraction: F1 / token overlap vs. ground truth.

For summarize: similarity to reference, or LLM-judged alignment.

Operational:

Latency, error rate, token usage, cost per 1k rows.

Safety & quality:

Toxicity heuristics, PII leakage heuristics, etc.

All of that is invisible to clx; clx just sends requests.

4. Treat batches and runs as first-class objects

Databricks talks about “production workflows,” “batch inference,” and they surface billing & performance using system tables. 
Microsoft Learn

For your backend, I’d define:

Run: a logical grouping (e.g., that Spark job, or that notebook cell run):

run_id, run_name, owner, start_ts, end_ts, source, status, counts.

Observation: a single model call within a run:

observation_id, run_id, input_hash, output_hash, eval_scores.

clx can:

Auto-generate run_id per process or per explicit “session.”

Pass run_id in context.

Let advanced users override run_id to link multiple jobs.

Backend can then:

Aggregate by run_id for dashboards:

success/failure, average latency, average eval scores.

Support queries like:

“Show me eval metrics for yesterday’s weekly summarization job.”

“Compare eval scores for modelA vs modelB for the same run type.”

5. Observability: logs, metrics, and traces around eval

Databricks gives query profiles and cost visibility via system tables. 
Microsoft Learn

You can take it further by:

Logging one row per observation into a warehouse table:

timestamp, run_id, observation_id, model, task, prompt_hash, response_hash, latency, tokens, cost, eval_scores (JSON).

Emitting metrics to something like Prometheus / OTEL:

clx_requests_total{model=..., task=...}

clx_eval_score_avg{metric="accuracy", task="classify"}

With eval tied to each observation, metrics are grounded in quality, not just usage.

6. Design clx’s API so eval is easy to opt into

On the clx side, you don’t implement eval, but you do give people ways to:

Set eval policy quickly:

clx_query(
    model="my-model",
    prompt="...",
    params={"max_tokens": 128},
    context={"eval_policy": "default"}
)


Pass tags that the backend can use for routing/experiments:

clx_query(
    model="my-model",
    prompt="...",
    params={...},
    context={"tags": ["experiment:ab-v3", "pipeline:billing"]}
)


In Spark:

SELECT clx_query(
  'my-model',
  CONCAT('Summarize: ', text),
  named_struct('max_tokens', 100, 'temperature', 0.3, 'eval_policy', 'default')
) AS summary
FROM ...


You can implement this by allowing modelParameters/params to have a reserved sub-struct, e.g. clx_context, which clx peels off and passes as context in the HTTP body.

7. Model & routing logic as “backend strategies”

Databricks has pre-deployed models, BYO models, external models, etc., and ai_query abstracts over all of them. 
Microsoft Learn

You can mimic the power but keep it totally in the backend:

model is a logical name: “summarizer-v1”, “extractor:v2”, “my-bert-ner”.

Backend maps that to:

A specific foundation model endpoint,

A chain (e.g., reranker, or pre-/post-processing),

Or even a traditional ML model (like their spam example). 
Microsoft Learn

Eval is then attached to strategies, not just raw models:

strategy: summarizer-v1 uses eval policy summarizer-default.

strategy: summarizer-v2 uses summarizer-experiment-ab.

You can test multiple strategies live with the same clx_query call by routing based on context tags or traffic splits.

8. Putting it all together: one concrete flow

User runs in Databricks:

df_out = df.selectExpr(
  "clx_query("
  "  'summarizer-v1', "
  "  CONCAT('Summarize: ', text), "
  "  named_struct('max_tokens', 120, 'temperature', 0.3, 'eval_policy', 'default')"
  ") as summary"
)


clx UDF:

Extracts model, prompt, modelParameters.

Splits params (modelParams) and context (eval_policy, maybe run_id, tags).

Calls your backend:

{
  "model": "summarizer-v1",
  "prompt": "Summarize: ...",
  "params": {"max_tokens": 120, "temperature": 0.3},
  "context": {
    "source": "spark_sql",
    "function": "clx_query",
    "eval_policy": "default",
    "run_id": "job-1234",
    "dataset": "catalog.schema.table"
  }
}


Backend:

Resolves summarizer-v1 to some actual hosted model.

Logs an observation row (with pending_eval=true).

Calls the model, returns output immediately.

Queues eval work (or runs inline) per eval_policy.

Writes eval metrics back into the same observation row.

Downstream:

You query an observations/evals table to see:

Accuracy vs ground truth,

Latency distributions,

Cost & quality per strategy/model,

Drift over time.

clx stays as a small, boring library. The backend becomes the place where you can iterate on quality, observability, and governance fast, without users ever changing their SQL or Python call signatures.

If you’d like, I can draft a minimal JSON schema for your Observation + Evaluation tables and a stub FastAPI /v1/query that already does logging + a pluggable eval pipeline.
