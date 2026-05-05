<!-- Description: CA-S07 checklist for legacy diagnostics/template fallback strip and LC-08 cleanup verification. -->
<!-- Version: 2026.05.05.1 -->
<!-- Last updated: 2026-05-05 -->

# CA-S07 Legacy Diagnostics/Template Fallback Cleanup Checklist

## Scope

- Slice: `CA-S07`
- Domain: `LC-08` legacy diagnostics/template fallback retirement
- Objective: verify component-first diagnostics/template consumers and close legacy fallback references with deterministic evidence.

## Target cleanup lanes

- `LC8-L01` devtools templates runtime fallback references
- `LC8-L02` diagnostics templates runtime-fallback read branches
- `LC8-L03` operator quick-path docs fallback reference cleanup

## Required evidence packet fields

- `window_id`
- `captured_at`
- `component_first_consumers_ready`
- `legacy_fallback_reference_count`
- `fallback_reference_inventory`
- `required_component_surface_count`
- `resolved_component_surface_count`
- `runtime_fallback_hits`
- `blocking_reasons`
- `verdict`
- `next_action`

## CA-S07 pass policy

CA-S07 is `READY` only when:

1. component-first consumer surfaces are available for all required diagnostics lanes,
2. remaining legacy fallback references are explicitly inventoried,
3. runtime fallback hits are either zero or explicitly justified for bounded compatibility windows,
4. blocker taxonomy is deterministic,
5. missing required evidence fails closed.

## Blocker taxonomy

- `component_surface_missing`
- `legacy_reference_unclassified`
- `fallback_hits_unexplained`
- `missing_required_evidence`

## Two-track disposition

- Runtime track: `compatibility-shimmed` until legacy diagnostics/template references are fully retired or explicitly deferred
- Component track: `implemented` with component-first diagnostics/template surfaces active and consumable

## Closeout recommendation rule

- `READY`: required component surfaces resolved, legacy references classified, no blockers.
- `HOLD`: references remain but are classified with bounded compatibility rationale.
- `BLOCKED`: any blocker taxonomy hit or required evidence missing.
