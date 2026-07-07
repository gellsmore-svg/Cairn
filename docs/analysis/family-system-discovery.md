# System Observation Discovery: /home/cello/domains

## Surfaces
- **Cairn** (process_language) - `/home/cello/domains/Cairn`
  - evidence: Cairn repo or UI scenario docs detected
  - observe: Use Cairn as the shared language for observer evidence, role-play, and annotations.
  - observe: Run cairn-ui-pipeline and cairn-live-observe to generate reviewable artifacts.
- **Ed** (uses_llm_queue) - `/home/cello/domains/Ed`
  - evidence: Hoglah dependency/reference detected
  - observe: Observe model-call submissions, job ids, retries, and queue latency where this product uses Hoglah.
  - observe: Join product events to Hoglah/Galeed correlation ids.
- **Galeed** (trace_log_spine) - `/home/cello/domains/Galeed`
  - evidence: Galeed package layout or package metadata
  - observe: Consume trace_events and llm_calls as primary live observation sources.
  - observe: Preserve request_id/session_id/trace_id/plan_id/job_id for cross-project joins.
- **Hanani** (uses_llm_queue) - `/home/cello/domains/Hanani`
  - evidence: Hoglah dependency/reference detected
  - observe: Observe model-call submissions, job ids, retries, and queue latency where this product uses Hoglah.
  - observe: Join product events to Hoglah/Galeed correlation ids.
- **Hoglah** (llm_queue) - `/home/cello/domains/Hoglah`
  - evidence: Hoglah package/name detected
  - observe: Observe queue depth, retries, failures, model latency, and stalled jobs.
  - observe: Join job_id to Galeed traces and Cairn process steps.
- **Mahalath** (uses_llm_queue) - `/home/cello/domains/Mahalath`
  - evidence: Hoglah dependency/reference detected
  - observe: Observe model-call submissions, job ids, retries, and queue latency where this product uses Hoglah.
  - observe: Join product events to Hoglah/Galeed correlation ids.
- **Mahlah** (ui_surface) - `/home/cello/domains/Mahlah`
  - evidence: package.json
  - evidence: e2e
  - observe: Run Playwright-backed Cairn UI scenarios for human-load evidence.
  - observe: Capture context switches, repair loops, missing information, and closure clarity.
- **Milcah** (uses_llm_queue) - `/home/cello/domains/Milcah`
  - evidence: Hoglah dependency/reference detected
  - observe: Observe model-call submissions, job ids, retries, and queue latency where this product uses Hoglah.
  - observe: Join product events to Hoglah/Galeed correlation ids.
- **Mizpah** (ui_surface) - `/home/cello/domains/Mizpah`
  - evidence: package.json
  - observe: Run Playwright-backed Cairn UI scenarios for human-load evidence.
  - observe: Capture context switches, repair loops, missing information, and closure clarity.
- **Noa** (runtime_host) - `/home/cello/domains/Noa`
  - evidence: versions.lock
  - evidence: compose.yaml
  - evidence: health/healthcheck.sh
  - observe: Run health checks and convert failures/latency into live observation events.
  - observe: Use Noa as the host for stack-wide observer agents, without embedding analysis logic in Noa.
- **Relational-Substrate** (ui_surface) - `/home/cello/domains/Relational-Substrate`
  - evidence: package.json
  - observe: Run Playwright-backed Cairn UI scenarios for human-load evidence.
  - observe: Capture context switches, repair loops, missing information, and closure clarity.
- **Tirzah** (uses_llm_queue) - `/home/cello/domains/Tirzah`
  - evidence: Hoglah dependency/reference detected
  - observe: Observe model-call submissions, job ids, retries, and queue latency where this product uses Hoglah.
  - observe: Join product events to Hoglah/Galeed correlation ids.
- **codex** (ui_surface) - `/home/cello/domains/codex`
  - evidence: package.json
  - observe: Run Playwright-backed Cairn UI scenarios for human-load evidence.
  - observe: Capture context switches, repair loops, missing information, and closure clarity.

## Proposed Observation Plan
1. Create a small observation JSONL stream with source, kind, tags, duration_ms, and human_systems.
2. Bind Galeed trace/log events and LLM call records into the observation stream.
3. Author or run Playwright/Cairn UI scenarios for key human workflows.
4. Add queue-health observations for LLM jobs, retries, failures, and latency.
5. Join product-level agent steps to Hoglah queue events and Galeed trace ids.
6. Run the observer from the runtime host so cross-project health and correlation keys are visible.
7. Generate Cairn evidence, role-play critique, and annotation snippets for review.
8. Cluster repeated findings into product issues or process-improvement proposals.