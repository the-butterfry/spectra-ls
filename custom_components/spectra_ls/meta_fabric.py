# Description: Meta fabric startup-orchestration workflow for Spectra LS metadata recovery and MA boot-gate readiness semantics.
# Version: 2026.05.04.1
# Last updated: 2026-05-04
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any

from .event_recovery_fabric import EventRecoveryFabricWorkflow
from .scaffold_fabric import ScaffoldFabricWorkflow
from .selection_fabric import SelectionFabricWorkflow
from .startup_recovery_fabric import StartupRecoveryFabricWorkflow
from .validation_fabric import ValidationFabricWorkflow


class MetaFabricWorkflow:
    """Owns metadata startup recovery orchestration extracted from coordinator."""

    def __init__(self, coordinator: Any) -> None:
        self._coordinator = coordinator
        self._selection_fabric = SelectionFabricWorkflow(coordinator)
        self._validation_fabric = ValidationFabricWorkflow(coordinator, self._selection_fabric)
        self._startup_recovery_fabric = StartupRecoveryFabricWorkflow(coordinator)
        self._event_recovery_fabric = EventRecoveryFabricWorkflow(coordinator)
        self._scaffold_fabric = ScaffoldFabricWorkflow(
            coordinator,
            self._selection_fabric,
            self._validation_fabric,
        )

    async def async_schedule_startup_recovery(self) -> None:
        """Schedule bounded post-startup recovery for target/options and bridge alignment."""
        await self._startup_recovery_fabric.async_schedule_startup_recovery()

    def handle_startup_recovery_timer(self, _now) -> None:
        """Kick off one startup recovery attempt from timer callback."""
        self._startup_recovery_fabric.handle_startup_recovery_timer(_now)

    async def async_run_startup_recovery_attempt(self) -> None:
        """Run one bounded startup recovery attempt and schedule retry if needed."""
        await self._startup_recovery_fabric.async_run_startup_recovery_attempt()

    def is_startup_recovery_boot_ready(self) -> tuple[bool, list[str]]:
        """Return whether MA/runtime surfaces are ready for startup recovery attempts."""
        return self._startup_recovery_fabric.is_startup_recovery_boot_ready()

    @staticmethod
    def startup_wait_reason_prefix(reasons: list[str]) -> str:
        """Return human-readable startup wait prefix aligned to the blocking phase."""
        return StartupRecoveryFabricWorkflow.startup_wait_reason_prefix(reasons)

    @staticmethod
    def format_startup_boot_wait_reasons(reasons: list[str]) -> str:
        """Format startup readiness blockers into operator-friendly wait messaging."""
        return StartupRecoveryFabricWorkflow.format_startup_boot_wait_reasons(reasons)

    def build_metadata_validation_bundle(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build metadata prep/bridge/cutover validation bundle for snapshot assembly."""
        return self._validation_fabric.build_metadata_validation_bundle(
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def normalize_metadata_validation_bundle(
        self,
        metadata_bundle: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        """Normalize metadata validation bundle payload shapes for snapshot assembly."""
        return self._validation_fabric.normalize_metadata_validation_bundle(metadata_bundle)

    def build_write_controls_metadata_surfaces(self) -> dict[str, Any]:
        """Build metadata-related write-control surfaces for coordinator snapshot payload."""
        return self._validation_fabric.build_write_controls_metadata_surfaces()

    def build_meta_policy_surface(self) -> dict[str, Any]:
        """Build metadata policy surface from helpers/defaults for write-controls payload."""
        return self._validation_fabric.build_meta_policy_surface()

    def evaluate_handoff_scaffold_statuses(
        self,
        *,
        component_scaffolds: dict[str, Any],
        target_options_attempt: dict[str, Any],
        auto_select_attempt: dict[str, Any],
        metadata_attempt: dict[str, Any],
        metadata_bridge_attempt: dict[str, Any],
    ) -> dict[str, str]:
        """Evaluate handoff scaffold status ladder for target-options, auto-select, and metadata lanes."""
        return self._validation_fabric.evaluate_handoff_scaffold_statuses(
            component_scaffolds=component_scaffolds,
            target_options_attempt=target_options_attempt,
            auto_select_attempt=auto_select_attempt,
            metadata_attempt=metadata_attempt,
            metadata_bridge_attempt=metadata_bridge_attempt,
        )

    def build_handoff_dependency_map(
        self,
        *,
        target_options_status: str,
        auto_select_status: str,
        metadata_status: str,
    ) -> list[dict[str, Any]]:
        """Build handoff dependency map rows from scaffold-status surfaces."""
        return self._validation_fabric.build_handoff_dependency_map(
            target_options_status=target_options_status,
            auto_select_status=auto_select_status,
            metadata_status=metadata_status,
        )

    def build_scheduler_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build scheduler readiness and default-decision validation payload."""
        return self._validation_fabric.build_scheduler_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def build_contract_validation(self) -> dict[str, Any]:
        """Build required/soft contract validation payload for routing surfaces."""
        return self._validation_fabric.build_contract_validation()

    def build_selection_handoff_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build selection-handoff compatibility/guard validation payload."""
        return self._validation_fabric.build_selection_handoff_validation(
            parity=parity,
            route_trace=route_trace,
            contract_validation=contract_validation,
        )

    def build_route_safety_validation(
        self,
        *,
        parity: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Build explicit route-safety diagnostics for active-target binding and host posture."""
        return self._validation_fabric.build_route_safety_validation(
            parity=parity,
            route_trace=route_trace,
        )

    def build_host_control_cutover_gate(
        self,
        *,
        parity: dict[str, Any],
        registry: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute deterministic host-control cutover readiness for component authority windows."""
        return self._validation_fabric.build_host_control_cutover_gate(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )

    def build_control_center_validation(self) -> dict[str, Any]:
        """Build control-center settings and execution-readiness diagnostics payload."""
        return self._validation_fabric.build_control_center_validation()

    def build_capability_profile_validation(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        metadata_prep_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build F4-S01 capability/profile validation packet from registry + route surfaces."""
        return self._validation_fabric.build_capability_profile_validation(
            registry=registry,
            route_trace=route_trace,
            contract_validation=contract_validation,
            metadata_prep_validation=metadata_prep_validation,
        )

    def build_action_catalog_validation(
        self,
        *,
        registry: dict[str, Any],
        contract_validation: dict[str, Any],
        capability_profile_validation: dict[str, Any],
    ) -> dict[str, Any]:
        """Build F4-S02 action-catalog validation packet from capability/profile diagnostics."""
        return self._validation_fabric.build_action_catalog_validation(
            registry=registry,
            contract_validation=contract_validation,
            capability_profile_validation=capability_profile_validation,
        )

    def build_crossfade_balance_validation(
        self,
        *,
        route_trace: dict[str, Any],
        contract_validation: dict[str, Any],
        action_catalog_validation: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build F4-S03 crossfade/balance validation packet from route + action diagnostics."""
        return self._validation_fabric.build_crossfade_balance_validation(
            route_trace=route_trace,
            contract_validation=contract_validation,
            action_catalog_validation=action_catalog_validation,
        )

    def build_snapshot_validation_packet(
        self,
        *,
        parity: dict[str, Any],
        registry: dict[str, Any],
        route_trace: dict[str, Any],
    ) -> dict[str, Any]:
        """Build packetized snapshot-validation surfaces for coordinator snapshot assembly."""
        return self._validation_fabric.build_snapshot_validation_packet(
            parity=parity,
            registry=registry,
            route_trace=route_trace,
        )

    def build_component_scaffolds(self) -> dict[str, Any]:
        """Build component-native scaffold plans for selection/metadata ownership handoff."""
        return self._scaffold_fabric.build_component_scaffolds()

    def compute_component_target_options_plan(self) -> dict[str, Any]:
        """Compute deterministic component target-options plan from helpers/registry/runtime surfaces."""
        return self._selection_fabric.compute_component_target_options_plan()

    def compute_scheduler_decision(
        self,
        *,
        registry: dict[str, Any],
        route_trace: dict[str, Any],
        policy: dict[str, Any],
    ) -> dict[str, Any]:
        """Compute deterministic scheduler ranking and selected candidate payload."""
        return self._selection_fabric.compute_scheduler_decision(
            registry=registry,
            route_trace=route_trace,
            policy=policy,
        )

    def build_handoff_inventory(self) -> dict[str, Any]:
        """Build legacy dependency and scaffold-status handoff inventory packet."""
        return self._scaffold_fabric.build_handoff_inventory()

    def build_ma_backend_profile(self) -> dict[str, Any]:
        """Build MA backend profile/effective URL diagnostics payload."""
        return self._scaffold_fabric.build_ma_backend_profile()

    async def async_run_scheduler_choice(
        self,
        *,
        require_control_capable: bool,
        prefer_fresh: bool,
        max_results: int,
        target_hint: str,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run scheduler ranking against current registry/profile snapshot and store decision payload."""
        return await self._selection_fabric.async_run_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            correlation_id=correlation_id,
        )

    async def async_apply_scheduler_choice(
        self,
        *,
        require_control_capable: bool,
        prefer_fresh: bool,
        max_results: int,
        target_hint: str,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run scheduler decision and guardedly apply selected target to helper entity."""
        return await self._selection_fabric.async_apply_scheduler_choice(
            require_control_capable=require_control_capable,
            prefer_fresh=prefer_fresh,
            max_results=max_results,
            target_hint=target_hint,
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def async_build_target_options_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Build (and optionally apply) component-native target-options scaffold plan."""
        return await self._selection_fabric.async_build_target_options_scaffold(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def async_run_auto_select_scaffold(
        self,
        *,
        dry_run: bool,
        force: bool,
        sync_options_if_missing: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Run component-native auto-select scaffold with guarded helper apply semantics."""
        return await self._selection_fabric.async_run_auto_select_scaffold(
            dry_run=dry_run,
            force=force,
            sync_options_if_missing=sync_options_if_missing,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def async_track_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
        source: str = "service_track_last_valid_target",
    ) -> dict[str, Any]:
        """Track helper-selected target into last-valid helper with guarded writes."""
        return await self._selection_fabric.async_track_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
            source=source,
        )

    async def async_restore_last_valid_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Restore helper selection from last-valid helper when current selection is unresolved."""
        return await self._selection_fabric.async_restore_last_valid_target(
            dry_run=dry_run,
            force=force,
            correlation_id=correlation_id,
        )

    async def async_cycle_active_target(
        self,
        *,
        dry_run: bool,
        force: bool,
        include_none: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Cycle active-target helper options with optional none filtering and override activation."""
        return await self._selection_fabric.async_cycle_active_target(
            dry_run=dry_run,
            force=force,
            include_none=include_none,
            correlation_id=correlation_id,
        )

    async def async_set_active_target(
        self,
        *,
        target: str,
        dry_run: bool,
        force: bool,
        sync_options_if_missing: bool,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        """Set active-target helper selection through component-guarded explicit target contract."""
        return await self._selection_fabric.async_set_active_target(
            target=target,
            dry_run=dry_run,
            force=force,
            sync_options_if_missing=sync_options_if_missing,
            correlation_id=correlation_id,
        )

    def auto_select_loop_preflight(self) -> tuple[bool, str]:
        """Return whether component auto-select loop can run in current authority/runtime state."""
        return self._event_recovery_fabric.auto_select_loop_preflight()

    async def async_run_component_auto_select_loop(self, *, source: str, force: bool = False) -> None:
        """Run component-side auto-select loop parity behavior under guarded semantics."""
        await self._event_recovery_fabric.async_run_component_auto_select_loop(source=source, force=force)

    async def async_run_component_players_change_refresh(self, *, source: str) -> None:
        """Mirror legacy players-change sequencing: refresh options, then auto-select."""
        await self._event_recovery_fabric.async_run_component_players_change_refresh(source=source)

    async def async_apply_ambiguity_lock(self, *, source: str) -> None:
        """Mirror legacy lock-on-ambiguous-select behavior for component authority windows."""
        await self._event_recovery_fabric.async_apply_ambiguity_lock(source=source)

    async def async_apply_stale_unlock(self, *, source: str) -> None:
        """Mirror legacy stale-meta unlock behavior with bounded auto-select follow-up."""
        await self._event_recovery_fabric.async_apply_stale_unlock(source=source)

    def handle_meta_stale_unlock_timer(self, _now) -> None:
        """Handle delayed stale unlock hold callback."""
        self._event_recovery_fabric.handle_meta_stale_unlock_timer(_now)

    async def async_dismiss_no_control_feedback_notification(self) -> None:
        """Dismiss no-control feedback notification if present."""
        await self._event_recovery_fabric.async_dismiss_no_control_feedback_notification()

    def handle_no_control_feedback_hold_timer(self, _now) -> None:
        """Start self-heal sequence after no-control feedback hold timer."""
        self._event_recovery_fabric.handle_no_control_feedback_hold_timer(_now)

    async def async_run_no_control_feedback_self_heal(self) -> None:
        """Run bounded self-heal sequence for no-control-capable-hosts state."""
        await self._event_recovery_fabric.async_run_no_control_feedback_self_heal()

    def handle_no_control_feedback_post_heal_timer(self, _now) -> None:
        """Handle post-heal delay timer before creating notification."""
        self._event_recovery_fabric.handle_no_control_feedback_post_heal_timer(_now)

    async def async_finalize_no_control_feedback_notification(self) -> None:
        """Create final no-control feedback notification when state persists after self-heal."""
        await self._event_recovery_fabric.async_finalize_no_control_feedback_notification()

    def handle_global_state_change(self, event) -> None:
        """Mirror legacy event-based auto-select trigger for watched target entities."""
        self._event_recovery_fabric.handle_global_state_change(event)

    def handle_state_change(self, event) -> None:
        """Handle state-change orchestration lane for event/recovery parity behaviors."""
        self._event_recovery_fabric.handle_state_change(event)