<!-- Description: CA-S05 checklist for ESP listener soak evidence and readiness evaluation. -->
<!-- Version: 2026.08.01.1 -->
<!-- Last updated: 2026-08-01 -->

# CA-S05 ESP Listener Soak Checklist

Use this checklist for integration-first listener soak validation and readiness evidence capture.

## Required evidence

- sustained healthy listener operation over the target soak window
- stable contract outputs in component and runtime consumer lanes
- clear blocker list when readiness is not achieved

## Output packet

- soak window start/end
- primary health counters
- readiness verdict (`ready` / `not_ready`)
- deterministic next action
