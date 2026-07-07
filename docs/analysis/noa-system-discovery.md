# System Observation Discovery: /home/cello/domains/Noa

## Surfaces
- **Noa** (runtime_host) - `/home/cello/domains/Noa`
  - evidence: versions.lock
  - evidence: compose.yaml
  - evidence: health/healthcheck.sh
  - observe: Run health checks and convert failures/latency into live observation events.
  - observe: Use Noa as the host for stack-wide observer agents, without embedding analysis logic in Noa.

## Proposed Observation Plan
1. Create a small observation JSONL stream with source, kind, tags, duration_ms, and human_systems.
2. Run the observer from the runtime host so cross-project health and correlation keys are visible.
3. Cluster repeated findings into product issues or process-improvement proposals.