# Description: Contract-shape regression tests for Spectra LS metadata/selection/validation workflows.
# Version: 2026.08.18.4
# Last updated: 2026-08-18

from __future__ import annotations

import asyncio
import unittest

from tests.spectra_ls_contracts.harness import FakeCoordinator, FakeHass, FakeState, load_spectra_modules


class SpectraContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        modules = load_spectra_modules()
        cls.MetadataStackWorkflow = modules["metadata_stack"].MetadataStackWorkflow
        cls.SelectionFabricWorkflow = modules["selection_fabric"].SelectionFabricWorkflow
        cls.ValidationFabricWorkflow = modules["validation_fabric"].ValidationFabricWorkflow

    def test_metadata_cutover_prep_contract_contains_expected_keys(self) -> None:
        coordinator = FakeCoordinator()
        workflow = self.MetadataStackWorkflow(coordinator)
        workflow._last_metadata_trial_attempt = {"eligible_for_closeout": False}
        workflow._last_metadata_bridge_attempt = {}

        packet = workflow.build_cutover_prep_validation(
            metadata_prep_validation={
                "metadata_authority_owner": "legacy_contract_surfaces",
                "metadata_cutover_active": False,
                "cutover_block_reason": "metadata_prep_not_ready",
                "ready_for_metadata_handoff": False,
            },
            metadata_bridge_validation={
                "ready_for_bridge": False,
                "bridge_status": "never_attempted",
                "trial_status": "never_attempted",
            },
        )

        self.assertEqual(packet.get("verdict"), "WARN")
        self.assertIn("checks", packet)
        self.assertIn("blocking_reasons", packet)
        self.assertIn("metadata_owner_not_component", packet.get("blocking_reasons", []))
        self.assertIn("cutover_proof_pre_window_missing", packet.get("blocking_reasons", []))

    def test_selection_scheduler_decision_contract_shape(self) -> None:
        coordinator = FakeCoordinator(
            hass=FakeHass(
                {
                    "input_select.ma_active_target": FakeState(
                        state="media_player.room_a",
                        attributes={"options": ["none", "media_player.room_a", "media_player.room_b"]},
                    )
                }
            )
        )
        workflow = self.SelectionFabricWorkflow(coordinator)

        packet = workflow.compute_scheduler_decision(
            registry={
                "entries": {
                    "media_player.room_a": {
                        "host": "192.168.1.20",
                        "control_capable": True,
                        "feature_profile": {
                            "availability_quality": "fresh",
                            "observed_capabilities": ["play", "pause"],
                        },
                        "empirical_profile": {"bonus": 1.5},
                    },
                    "media_player.room_b": {
                        "host": "",
                        "control_capable": True,
                        "feature_profile": {
                            "availability_quality": "missing",
                            "observed_capabilities": [],
                        },
                        "empirical_profile": {},
                    },
                }
            },
            route_trace={"active_target": "media_player.room_a"},
            policy={
                "require_control_capable": True,
                "prefer_fresh": True,
                "max_results": 5,
                "target_hint": "room_a",
            },
        )

        self.assertEqual(packet.get("status"), "selected")
        self.assertIn("policy", packet)
        self.assertIn("selected_target", packet)
        self.assertIn("ranked_candidates", packet)
        self.assertGreaterEqual(int(packet.get("candidate_count", 0)), 1)

    def test_validation_crossfade_warns_when_f4_s02_not_ready(self) -> None:
        coordinator = FakeCoordinator()
        selection_workflow = self.SelectionFabricWorkflow(coordinator)
        workflow = self.ValidationFabricWorkflow(coordinator, selection_workflow)

        packet = workflow.build_crossfade_balance_validation(
            route_trace={"decision": "route_linkplay_tcp", "active_target": "media_player.room_a"},
            contract_validation={"valid": True},
            action_catalog_validation={"ready_for_f4_s02": False},
        )

        self.assertEqual(packet.get("verdict"), "WARN")
        blockers = packet.get("dependency_reference", {}).get("blocking_reasons", [])
        self.assertIn("f4_s02_not_ready", blockers)
        self.assertIn("checks", packet)

    def test_metadata_bridge_recovers_stale_wait_status_after_boot_ready(self) -> None:
        coordinator = FakeCoordinator()
        workflow = self.MetadataStackWorkflow(coordinator)
        workflow._last_metadata_resolver_attempt = {"status": "dry_run_ok"}
        workflow._last_metadata_trial_attempt = {"status": "dry_run_ok"}
        workflow._last_metadata_bridge_attempt = {
            "status": "waiting_for_ma_boot",
            "reason": "",
            "stages": {},
        }

        packet = workflow.build_metadata_bridge_validation(
            metadata_prep_validation={
                "ready_for_metadata_handoff": True,
                "metadata_cutover_active": True,
                "values": {
                    "now_playing_entity": "media_player.room_a",
                },
            }
        )

        self.assertEqual(
            packet.get("bridge_status"),
            "startup_readiness_recovered_pending_bridge_attempt",
        )
        self.assertTrue(packet.get("last_bridge_attempt", {}).get("startup_readiness_recovered", False))

    def test_action_catalog_validation_contract_summary_shape(self) -> None:
        coordinator = FakeCoordinator()
        selection_workflow = self.SelectionFabricWorkflow(coordinator)
        workflow = self.ValidationFabricWorkflow(coordinator, selection_workflow)

        packet = workflow.build_action_catalog_validation(
            registry={
                "entries": {
                    "media_player.room_a": {
                        "capabilities": ["play", "pause", "volume_set"],
                    }
                }
            },
            contract_validation={"valid": True},
            capability_profile_validation={"ready_for_f4_s01": True, "profile_schema": {"schema_version": "f4_s01.v1"}},
        )

        self.assertEqual(packet.get("verdict"), "PASS")
        self.assertTrue(packet.get("ready_for_f4_s02", False))
        summary = packet.get("catalog_summary", {})
        self.assertIn("action_count", summary)
        self.assertIn("capability_pool", summary)
        self.assertGreaterEqual(int(summary.get("action_count", 0)), 1)

    def test_route_safety_fails_on_selected_target_mismatch(self) -> None:
        coordinator = FakeCoordinator()
        selection_workflow = self.SelectionFabricWorkflow(coordinator)
        workflow = self.ValidationFabricWorkflow(coordinator, selection_workflow)

        packet = workflow.build_route_safety_validation(
            parity={
                "active_target": "media_player.room_a",
                "control_hosts": "192.168.1.20",
            },
            route_trace={
                "decision": "route_linkplay_tcp",
                "selected_target": {
                    "target": "media_player.room_b",
                    "host": "192.168.1.21",
                },
            },
        )

        self.assertEqual(packet.get("verdict"), "FAIL")
        self.assertIn("selected_target_mismatch", packet.get("blocking_reasons", []))

    def test_scheduler_validation_fails_when_route_trace_missing(self) -> None:
        coordinator = FakeCoordinator()
        selection_workflow = self.SelectionFabricWorkflow(coordinator)
        workflow = self.ValidationFabricWorkflow(coordinator, selection_workflow)

        packet = workflow.build_scheduler_validation(
            registry={
                "entries": {
                    "media_player.room_a": {
                        "host": "192.168.1.20",
                        "control_capable": True,
                        "feature_profile": {
                            "availability_quality": "fresh",
                            "observed_capabilities": ["play"],
                        },
                        "empirical_profile": {},
                    }
                }
            },
            route_trace={},
            contract_validation={"valid": True},
        )

        self.assertEqual(packet.get("verdict"), "FAIL")
        self.assertIn("route_trace_missing", packet.get("blocking_reasons", []))

    def test_set_active_target_dry_run_contract(self) -> None:
        coordinator = FakeCoordinator(
            hass=FakeHass(
                {
                    "input_select.ma_active_target": FakeState(
                        state="media_player.room_a",
                        attributes={"options": ["media_player.room_a", "media_player.room_b"]},
                    )
                }
            )
        )
        workflow = self.SelectionFabricWorkflow(coordinator)

        packet = asyncio.run(
            workflow.async_set_active_target(
                target="media_player.room_b",
                dry_run=True,
                force=False,
                sync_options_if_missing=False,
                correlation_id="test-dry-run",
            )
        )

        self.assertEqual(packet.get("status"), "dry_run_ok")
        self.assertEqual(packet.get("requested_target"), "media_player.room_b")

    def test_metadata_prep_keeps_source_label_for_passthrough_source_only(self) -> None:
        coordinator = FakeCoordinator(
            hass=FakeHass(
                {
                    "media_player.kitchen_wiim": FakeState(
                        state="idle",
                        attributes={
                            "source": "Optical In",
                            "friendly_name": "Kitchen Speakers",
                        },
                    ),
                    "sensor.component_now_playing_entity": FakeState(state="media_player.kitchen_wiim"),
                }
            )
        )
        workflow = self.MetadataStackWorkflow(coordinator)

        packet = workflow.build_metadata_prep_validation(
            route_trace={
                "active_target": "media_player.kitchen_wiim",
                "decision": "route_linkplay_tcp",
            },
            contract_validation={"valid": True},
        )

        values = packet.get("values", {})
        checks = packet.get("checks", {})
        self.assertEqual(values.get("now_playing_source"), "Optical In")
        self.assertEqual(values.get("now_playing_app"), "Optical In")
        self.assertTrue(bool(checks.get("passthrough_source_only_keepalive_ready", False)))
        self.assertEqual(values.get("canonical_oled_posture"), "passthrough_no_track_metadata")
        self.assertFalse(bool(values.get("now_playing_oled_blank_contract", True)))


if __name__ == "__main__":
    unittest.main()
