# Description: Lightweight test harness utilities for isolated Spectra LS contract tests.
# Version: 2026.08.18.4
# Last updated: 2026-08-18

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
import importlib.util
from pathlib import Path
import sys
import types
from typing import Any


@dataclass
class FakeState:
    state: str
    attributes: dict[str, Any] = field(default_factory=dict)
    last_changed: datetime | None = None
    last_updated: datetime | None = None

    def __post_init__(self) -> None:
        now = datetime.now(UTC)
        if self.last_changed is None:
            self.last_changed = now
        if self.last_updated is None:
            self.last_updated = now


class FakeStateStore:
    def __init__(self, mapping: dict[str, FakeState] | None = None) -> None:
        self._mapping = dict(mapping or {})

    def get(self, entity_id: str) -> FakeState | None:
        return self._mapping.get(entity_id)

    def async_all(self, domain: str) -> list[Any]:
        prefix = f"{domain}."
        rows: list[Any] = []
        for entity_id, state in self._mapping.items():
            if not entity_id.startswith(prefix):
                continue
            rows.append(
                types.SimpleNamespace(
                    entity_id=entity_id,
                    state=state.state,
                    attributes=state.attributes,
                    last_changed=state.last_changed,
                    last_updated=state.last_updated,
                )
            )
        return rows


class FakeHass:
    def __init__(self, mapping: dict[str, FakeState] | None = None) -> None:
        self.states = FakeStateStore(mapping)


class FakeCoordinator:
    def __init__(self, *, hass: FakeHass | None = None) -> None:
        self.hass = hass or FakeHass()
        self._write_authority_mode = "component"
        self._write_in_progress = False
        self._last_write_monotonic = 0.0
        self._write_debounce_s = 0.0
        self._component_selection_state: dict[str, Any] = {
            "active_target": "",
            "last_valid_target": "",
            "options": [],
            "updated_at": None,
            "source": "component_default_state",
        }
        self._last_write_attempt: dict[str, Any] = {}
        self._last_scheduler_decision: dict[str, Any] = {}
        self._last_set_active_target_attempt: dict[str, Any] = {}
        self.data: dict[str, Any] = {}
        self.utility_fabric = types.SimpleNamespace(
            extract_payload_list=lambda raw, _keys=None: raw if isinstance(raw, list) else []
        )
        self._scaffold_payload: dict[str, Any] = {
            "metadata_resolver_plan": {},
            "target_options_plan": {},
            "auto_select_plan": {},
        }

    @staticmethod
    def _availability_points(availability_quality: str) -> int:
        table = {
            "fresh": 20,
            "usable": 12,
            "stale": 6,
            "missing": 0,
        }
        return int(table.get(str(availability_quality or "missing"), 0))

    @staticmethod
    def _empirical_bonus(empirical_profile: dict[str, Any]) -> float:
        if not isinstance(empirical_profile, dict):
            return 0.0
        return float(empirical_profile.get("bonus", 0.0) or 0.0)

    @staticmethod
    def _normalize_state(value: Any) -> str:
        return str(value or "").strip().lower()

    @staticmethod
    def _is_resolved_state(value: Any) -> bool:
        norm = str(value or "").strip().lower()
        return norm not in {"", "none", "unknown", "unavailable", "null", "missing"}

    @staticmethod
    def _is_startup_recovery_boot_ready() -> tuple[bool, list[str]]:
        return True, []

    @staticmethod
    def _format_startup_boot_wait_reasons(reasons: list[str]) -> str:
        return ", ".join(reasons)

    def _build_component_scaffolds(self) -> dict[str, Any]:
        return dict(self._scaffold_payload)

    @staticmethod
    def _timestamp_age_seconds(value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            dt = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
            return max(0.0, (datetime.now(UTC) - dt.astimezone(UTC)).total_seconds())
        return None

    def _build_snapshot(self) -> dict[str, Any]:
        return dict(self.data)

    def async_set_updated_data(self, payload: dict[str, Any]) -> None:
        self.data = dict(payload)

    def refresh_snapshot(self) -> None:
        return



def _ensure_homeassistant_stubs() -> None:
    if "homeassistant.const" in sys.modules:
        return

    class Platform(str, Enum):
        SENSOR = "sensor"
        BINARY_SENSOR = "binary_sensor"

    homeassistant_mod = types.ModuleType("homeassistant")
    const_mod = types.ModuleType("homeassistant.const")
    const_mod.Platform = Platform
    homeassistant_mod.const = const_mod

    sys.modules["homeassistant"] = homeassistant_mod
    sys.modules["homeassistant.const"] = const_mod


def _ensure_namespace_packages(repo_root: Path) -> None:
    custom_components_mod = sys.modules.get("custom_components")
    if custom_components_mod is None:
        custom_components_mod = types.ModuleType("custom_components")
        custom_components_mod.__path__ = [str(repo_root / "custom_components")]
        sys.modules["custom_components"] = custom_components_mod

    spectra_pkg = sys.modules.get("custom_components.spectra_ls")
    if spectra_pkg is None:
        spectra_pkg = types.ModuleType("custom_components.spectra_ls")
        spectra_pkg.__path__ = [str(repo_root / "custom_components" / "spectra_ls")]
        sys.modules["custom_components.spectra_ls"] = spectra_pkg


def load_spectra_modules() -> dict[str, Any]:
    """Load Spectra workflow modules with isolated package/homeassistant stubs."""
    repo_root = Path(__file__).resolve().parents[2]
    module_root = repo_root / "custom_components" / "spectra_ls"

    _ensure_homeassistant_stubs()
    _ensure_namespace_packages(repo_root)

    module_order = [
        "const",
        "write_path_fabric",
        "metadata_selection_policy",
        "selection_fabric",
        "validation_fabric",
        "metadata_stack",
    ]

    loaded: dict[str, Any] = {}
    for module_name in module_order:
        fq_name = f"custom_components.spectra_ls.{module_name}"
        if fq_name in sys.modules:
            loaded[module_name] = sys.modules[fq_name]
            continue

        module_path = module_root / f"{module_name}.py"
        spec = importlib.util.spec_from_file_location(fq_name, module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load module: {fq_name}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[fq_name] = module
        spec.loader.exec_module(module)
        loaded[module_name] = module

    return loaded
