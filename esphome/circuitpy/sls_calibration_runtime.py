# Description: Runtime autocalibration/tracking state manager for Spectra LS RP2040 firmware.
# Version: 2026.08.24.6
# Last updated: 2026-08-24
#
# RP FILE CONTRACT:
# - Owns autocalibration trigger/channel/sample state and calibration tracking state.
# - Owns transitions and save decisions for calibration values.
# - Must NOT read hardware directly; caller supplies sampled values and time.
# - Must NOT change packet protocol or UART behavior.


class CalibrationRuntimeManager:
    def __init__(
        self,
        *,
        analog_inputs,
        calibration,
        save_calibration,
        calibration_missing,
        analog_name_for_index,
        analog_source_for_index,
        cfg,
        ticks_ms,
        ticks_diff,
        debug_calibration_serial=False,
    ):
        self.analog_inputs = analog_inputs
        self.calibration = calibration
        self.save_calibration = save_calibration
        self.calibration_missing = calibration_missing
        self.analog_name_for_index = analog_name_for_index
        self.analog_source_for_index = analog_source_for_index
        self.cfg = cfg
        self.ticks_ms = ticks_ms
        self.ticks_diff = ticks_diff
        self.debug_calibration_serial = debug_calibration_serial

        self.autocal_active = False
        self.autocal_channel_indices = []
        self.autocal_channel_pos = 0
        self.autocal_min = None
        self.autocal_max = None
        self.autocal_raw_min = None
        self.autocal_raw_max = None
        self.autocal_samples = []
        self.autocal_start_ms = 0
        self.autocal_source = None
        self.autocal_hold_start_ms = None
        self.autocal_triggered = False
        self.autocal_cooldown_until = 0
        self.autocal_armed = True

        self.tracking_indices = []
        self.tracking_min = {}
        self.tracking_max = {}
        self.tracking_min_ms = {}
        self.tracking_max_ms = {}
        self.tracking_low_hits = {}
        self.tracking_high_hits = {}
        self.tracking_samples = {}
        self.tracking_raw_samples = {}
        self.tracking_retry_after_ms = {}
        self.tracking_active = False

    def _tracking_force_save_samples_for_idx(self, idx):
        overrides = self.cfg.get("CALIBRATION_TRACKING_FORCE_SAVE_SAMPLES_BY_NAME") or {}
        name = self._name(idx)
        value = overrides.get(name)
        if value is None:
            return 0
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 0
        return parsed if parsed > 0 else 0

    def _tracking_force_min_range_for_idx(self, idx):
        overrides = self.cfg.get("CALIBRATION_TRACKING_FORCE_MIN_RANGE_BY_NAME") or {}
        name = self._name(idx)
        value = overrides.get(name)
        if value is None:
            return 0
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 0
        return parsed if parsed > 0 else 0

    def _tracking_min_range_for_idx(self, idx):
        default_value = int(self.cfg["CALIBRATION_TRACKING_MIN_RANGE"])
        overrides = self.cfg.get("CALIBRATION_TRACKING_MIN_RANGE_BY_NAME") or {}
        name = self._name(idx)
        value = overrides.get(name)
        if value is None:
            return default_value
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default_value
        return parsed if parsed > 0 else default_value

    def _tracking_edge_min_samples_for_idx(self, idx):
        default_value = int(self.cfg["CALIBRATION_TRACKING_EDGE_MIN_SAMPLES"])
        overrides = self.cfg.get("CALIBRATION_TRACKING_EDGE_MIN_SAMPLES_BY_NAME") or {}
        name = self._name(idx)
        value = overrides.get(name)
        if value is None:
            return default_value
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default_value
        return parsed if parsed >= 0 else default_value

    def _tracking_retry_delay_ms(self):
        value = self.cfg.get("CALIBRATION_TRACKING_RETRY_DELAY_MS", 1000)
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 1000
        return parsed if parsed >= 0 else 1000

    def _tracking_mid_min_samples(self):
        value = self.cfg.get("CALIBRATION_TRACKING_MID_MIN_SAMPLES", 40)
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 40
        return parsed if parsed > 0 else 40

    def _tracking_mid_samples_max(self):
        value = self.cfg.get("CALIBRATION_TRACKING_MID_SAMPLES_MAX", 400)
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 400
        return parsed if parsed > 0 else 400

    def _tracking_mid_enabled_for_idx(self, idx):
        name = self._name(idx)
        enabled = (self.cfg.get("CALIBRATION_TRACKING_ENABLE_MID_BY_NAME") or {}).get(name, False)
        return bool(enabled)

    def _tracking_calibration_requires_mid_refresh(self, idx):
        if not self._tracking_mid_enabled_for_idx(idx):
            return False
        source = self._source(idx)
        name = self._name(idx)
        existing = self.calibration.get(source, {}).get(name) or {}
        raw_min = existing.get("min")
        raw_max = existing.get("max")
        raw_mid = existing.get("mid")
        if raw_min is None or raw_max is None:
            return True
        return raw_mid is None

    def _tracking_record_sample(self, idx, raw):
        samples = self.tracking_raw_samples.setdefault(idx, [])
        samples.append(int(raw))
        max_samples = self._tracking_mid_samples_max()
        if len(samples) > max_samples:
            del samples[: len(samples) - max_samples]

    def _tracking_calibration_payload(self, idx, min_val, max_val):
        payload = {"min": int(min_val), "max": int(max_val)}
        if not self._tracking_mid_enabled_for_idx(idx):
            return payload
        samples = self.tracking_raw_samples.get(idx) or []
        if len(samples) < self._tracking_mid_min_samples():
            return payload
        ordered = sorted(samples)
        mid = ordered[len(ordered) // 2]
        span = max_val - min_val
        min_mid_guard = max(1, int(span * 0.02))
        if mid <= (min_val + min_mid_guard):
            mid = min_val + min_mid_guard
        if mid >= (max_val - min_mid_guard):
            mid = max_val - min_mid_guard
        if min_val < mid < max_val:
            payload["mid"] = int(mid)
        return payload

    def _name(self, idx):
        return self.analog_name_for_index(self.analog_inputs, idx)

    def _source(self, idx):
        return self.analog_source_for_index(self.analog_inputs, idx)

    def build_autocal_indices(self, names_override=None):
        if not self.cfg["AUTOCAL_ENABLED"]:
            return []
        if names_override:
            names = set(names_override)
        elif self.cfg["AUTOCAL_CHANNEL_NAMES"]:
            names = set(self.cfg["AUTOCAL_CHANNEL_NAMES"])
        else:
            names = None
        indices = []
        for idx in range(len(self.analog_inputs)):
            if not self.analog_inputs[idx].get("enabled", True):
                continue
            name = self._name(idx)
            if names and name not in names:
                continue
            indices.append(idx)
        return indices

    def current_autocal_index(self):
        if not self.autocal_channel_indices or self.autocal_channel_pos >= len(self.autocal_channel_indices):
            return None
        return self.autocal_channel_indices[self.autocal_channel_pos]

    def _begin_autocal_channel(self):
        self.autocal_min = None
        self.autocal_max = None
        self.autocal_raw_min = None
        self.autocal_raw_max = None
        self.autocal_samples = []
        self.autocal_start_ms = self.ticks_ms()
        idx = self.current_autocal_index()
        if idx is not None:
            name = self._name(idx)
            self.autocal_source = self._source(idx)
            if self.debug_calibration_serial:
                print(f"Auto-cal start: {name} ({self.autocal_source})")

    def _save_calibration(self):
        return self.save_calibration(
            self.calibration,
            self.cfg["CALIBRATION_ENABLED"],
            self.cfg["CALIBRATION_FILE"],
            self.debug_calibration_serial,
        )

    def _finish_autocal_channel(self):
        idx = self.current_autocal_index()
        if idx is None:
            self.autocal_active = False
            return

        name = self._name(idx)
        source = self.autocal_source or self._source(idx)
        sample_count = len(self.autocal_samples)

        if sample_count < self.cfg["AUTOCAL_MIN_SAMPLES"]:
            if self.debug_calibration_serial:
                print(f"Auto-cal failed: {name} not enough samples ({sample_count})")
        else:
            sorted_samples = sorted(self.autocal_samples)
            trim = int(sample_count * self.cfg["AUTOCAL_TRIM_PCT"] / 100)
            if trim * 2 >= sample_count:
                trim = 0
            trimmed = sorted_samples[trim: sample_count - trim]
            self.autocal_min = trimmed[0]
            self.autocal_max = trimmed[-1]
            if self.debug_calibration_serial:
                print(
                    f"Auto-cal samples={sample_count} raw_min={self.autocal_raw_min} raw_max={self.autocal_raw_max} "
                    f"trimmed_min={self.autocal_min} trimmed_max={self.autocal_max} trim={self.cfg['AUTOCAL_TRIM_PCT']}%"
                )

            span = int(self.autocal_max - self.autocal_min)
            if span < self.cfg["AUTOCAL_MIN_RANGE"]:
                if self.debug_calibration_serial:
                    print(f"Auto-cal failed: {name} span too small ({span})")
            else:
                edge_span = max(1, int(span * self.cfg["AUTOCAL_EDGE_PCT"] / 100))
                high_threshold = self.autocal_max - edge_span
                low_threshold = self.autocal_min + edge_span
                high_hits = 0
                low_hits = 0
                for sample in self.autocal_samples:
                    if sample >= high_threshold:
                        high_hits += 1
                    if sample <= low_threshold:
                        low_hits += 1

                headroom_high = self.cfg["AUTOCAL_HEADROOM_PCT"]
                headroom_low = 0
                if high_hits < self.cfg["AUTOCAL_EDGE_MIN_SAMPLES"]:
                    headroom_high += self.cfg["AUTOCAL_EDGE_HEADROOM_PCT"]
                if low_hits < self.cfg["AUTOCAL_EDGE_MIN_SAMPLES"]:
                    headroom_low += self.cfg["AUTOCAL_EDGE_HEADROOM_PCT"]

                pad_high = int(span * headroom_high / 100)
                pad_low = int(span * headroom_low / 100)
                adjusted_min = min(self.autocal_min + pad_low, self.autocal_max - 1)
                adjusted_max = max(adjusted_min + 1, self.autocal_max - pad_high)

                self.calibration.setdefault(source, {})
                self.calibration[source][name] = {
                    "min": int(adjusted_min),
                    "max": int(adjusted_max),
                }
                saved = self._save_calibration()
                if self.debug_calibration_serial:
                    if saved:
                        print(
                            f"Auto-cal saved: {name} min={int(adjusted_min)} max={int(adjusted_max)} "
                            f"(edge_hits low={low_hits} high={high_hits} headroom low={headroom_low}% high={headroom_high}%)"
                        )
                    else:
                        print(
                            f"Auto-cal computed (not saved): {name} min={int(adjusted_min)} max={int(adjusted_max)} "
                            f"(edge_hits low={low_hits} high={high_hits} headroom low={headroom_low}% high={headroom_high}%)"
                        )

        self.autocal_channel_pos += 1
        if self.autocal_channel_pos >= len(self.autocal_channel_indices):
            self.autocal_active = False
            if self.debug_calibration_serial:
                print("Auto-cal complete")
            return

        self._begin_autocal_channel()

    def start_autocalibration(self, names_override=None):
        if not self.cfg["AUTOCAL_ENABLED"]:
            return
        self.autocal_channel_indices = self.build_autocal_indices(names_override)
        if not self.autocal_channel_indices:
            if self.debug_calibration_serial:
                print("Auto-cal skipped: no enabled channels")
            return
        self.autocal_channel_pos = 0
        self.autocal_active = True
        self._begin_autocal_channel()

    def update_autocal_trigger(self, pressed):
        if not self.cfg["AUTOCAL_ENABLED"] or self.autocal_active:
            return
        now = self.ticks_ms()
        if self.ticks_diff(now, self.autocal_cooldown_until) < 0:
            return

        if pressed:
            if self.cfg["AUTOCAL_REQUIRE_RELEASE"] and not self.autocal_armed:
                return
            if self.autocal_hold_start_ms is None:
                self.autocal_hold_start_ms = now
            elif (
                not self.autocal_triggered
                and self.ticks_diff(now, self.autocal_hold_start_ms) >= self.cfg["AUTOCAL_TRIGGER_HOLD_MS"]
            ):
                self.autocal_triggered = True
                self.autocal_armed = False
                if self.debug_calibration_serial:
                    print("Auto-cal trigger detected")
                self.start_autocalibration()
                self.autocal_cooldown_until = (now + self.cfg["AUTOCAL_COOLDOWN_MS"]) & 0xFFFFFFFF
        else:
            self.autocal_hold_start_ms = None
            self.autocal_triggered = False
            if self.cfg["AUTOCAL_REQUIRE_RELEASE"]:
                self.autocal_armed = True

    def maybe_boot_autocal(self):
        if not (self.cfg["AUTOCAL_ENABLED"] and self.cfg["AUTOCAL_BOOT_IF_MISSING"]):
            return
        boot_names = self.cfg["AUTOCAL_BOOT_CHANNEL_NAMES"] or self.cfg["AUTOCAL_CHANNEL_NAMES"]
        missing = [name for name in (boot_names or []) if self.calibration_missing(self.calibration, name)]
        if missing:
            if self.debug_calibration_serial:
                print(f"Boot auto-cal: {', '.join(missing)}")
            self.start_autocalibration(missing)

    def init_calibration_tracking(self):
        if not self.cfg["CALIBRATION_TRACKING_ENABLED"]:
            return
        names = set(self.cfg["CALIBRATION_TRACKING_CHANNEL_NAMES"]) if self.cfg["CALIBRATION_TRACKING_CHANNEL_NAMES"] else None
        for idx in range(len(self.analog_inputs)):
            if not self.analog_inputs[idx].get("enabled", True):
                continue
            name = self._name(idx)
            if names and name not in names:
                continue
            if self.calibration_missing(self.calibration, name) or self._tracking_calibration_requires_mid_refresh(idx):
                self.tracking_indices.append(idx)
                source = self._source(idx)
                existing = self.calibration.get(source, {}).get(name) or {}
                if existing.get("min") is not None:
                    self.tracking_min[idx] = int(existing.get("min"))
                if existing.get("max") is not None:
                    self.tracking_max[idx] = int(existing.get("max"))
        self.tracking_active = bool(self.tracking_indices)
        if self.tracking_active and self.debug_calibration_serial:
            names_line = ", ".join(self._name(idx) for idx in self.tracking_indices)
            print(f"Calibration tracking enabled for: {names_line}")

    def update_calibration_tracking(self, idx, raw):
        if not self.tracking_active or idx not in self.tracking_indices:
            return
        now = self.ticks_ms()
        retry_after = self.tracking_retry_after_ms.get(idx)
        if retry_after is not None and self.ticks_diff(now, retry_after) < 0:
            return
        min_val = self.tracking_min.get(idx)
        max_val = self.tracking_max.get(idx)
        min_changed = False
        max_changed = False

        if min_val is None or raw < min_val:
            self.tracking_min[idx] = raw
            self.tracking_min_ms[idx] = now
            min_val = raw
            min_changed = True
        if max_val is None or raw > max_val:
            self.tracking_max[idx] = raw
            self.tracking_max_ms[idx] = now
            max_val = raw
            max_changed = True
        if min_changed:
            self.tracking_low_hits[idx] = 0
        if max_changed:
            self.tracking_high_hits[idx] = 0

        if min_val is None or max_val is None:
            return

        span = max_val - min_val
        self._tracking_record_sample(idx, raw)
        self.tracking_samples[idx] = self.tracking_samples.get(idx, 0) + 1
        min_range = self._tracking_min_range_for_idx(idx)
        force_samples = self._tracking_force_save_samples_for_idx(idx)
        force_min_range = self._tracking_force_min_range_for_idx(idx)
        force_ready = (
            force_samples > 0
            and self.tracking_samples.get(idx, 0) >= force_samples
            and span >= force_min_range
        )
        if span < min_range:
            if not force_ready:
                return
            if self.debug_calibration_serial:
                print(
                    f"Calibration tracking force-save gate satisfied: {self._name(idx)} "
                    f"samples={self.tracking_samples.get(idx, 0)} span={span}"
                )

        edge_span = max(1, int(span * self.cfg["CALIBRATION_TRACKING_EDGE_PCT"] / 100))
        if raw <= (min_val + edge_span):
            self.tracking_low_hits[idx] = self.tracking_low_hits.get(idx, 0) + 1
        if raw >= (max_val - edge_span):
            self.tracking_high_hits[idx] = self.tracking_high_hits.get(idx, 0) + 1

        edge_min_samples = self._tracking_edge_min_samples_for_idx(idx)
        if edge_min_samples > 0:
            if self.tracking_low_hits.get(idx, 0) < edge_min_samples:
                return
            if self.tracking_high_hits.get(idx, 0) < edge_min_samples:
                return

        if self.ticks_diff(now, self.tracking_min_ms.get(idx, now)) < self.cfg["CALIBRATION_TRACKING_SETTLE_MS"]:
            return
        if self.ticks_diff(now, self.tracking_max_ms.get(idx, now)) < self.cfg["CALIBRATION_TRACKING_SETTLE_MS"]:
            return

        if self._tracking_mid_enabled_for_idx(idx):
            sample_count = len(self.tracking_raw_samples.get(idx) or [])
            if sample_count < self._tracking_mid_min_samples():
                return

        name = self._name(idx)
        source = self._source(idx)
        self.calibration.setdefault(source, {})
        self.calibration[source][name] = self._tracking_calibration_payload(idx, min_val, max_val)
        saved = self._save_calibration()
        if saved:
            print(f"Calibration saved: {name} min={int(min_val)} max={int(max_val)}")
            self.tracking_samples.pop(idx, None)
            self.tracking_raw_samples.pop(idx, None)
            self.tracking_retry_after_ms.pop(idx, None)
            self.tracking_indices.remove(idx)
            self.tracking_active = bool(self.tracking_indices)
        else:
            print(f"Calibration NOT saved (USB mounted): {name} min={int(min_val)} max={int(max_val)}")
            self.tracking_retry_after_ms[idx] = (now + self._tracking_retry_delay_ms()) & 0xFFFFFFFF
        if self.debug_calibration_serial:
            if saved:
                print(f"Calibration tracking saved: {name} min={int(min_val)} max={int(max_val)}")
            else:
                print(f"Calibration tracking pending retry: {name} min={int(min_val)} max={int(max_val)}")

    def get_tracking_calibration(self, idx):
        if not self.cfg["CALIBRATION_TRACKING_DYNAMIC"]:
            return None
        min_val = self.tracking_min.get(idx)
        max_val = self.tracking_max.get(idx)
        if min_val is None or max_val is None:
            return None
        min_range = self._tracking_min_range_for_idx(idx)
        if (max_val - min_val) < min_range:
            return None
        edge_min_samples = self._tracking_edge_min_samples_for_idx(idx)
        if edge_min_samples > 0:
            if self.tracking_low_hits.get(idx, 0) < edge_min_samples:
                return None
            if self.tracking_high_hits.get(idx, 0) < edge_min_samples:
                return None
        return {"min": int(min_val), "max": int(max_val)}

    def process_autocal_sample(self, idx, raw, now_ms):
        current_idx = self.current_autocal_index()
        if not (self.autocal_active and current_idx == idx):
            return False

        if self.ticks_diff(now_ms, self.autocal_start_ms) >= self.cfg["AUTOCAL_SETTLE_MS"]:
            self.autocal_samples.append(raw)
            if len(self.autocal_samples) > self.cfg["AUTOCAL_SAMPLE_LIMIT"]:
                self.autocal_samples.pop(0)
            if self.autocal_raw_min is None or raw < self.autocal_raw_min:
                self.autocal_raw_min = raw
            if self.autocal_raw_max is None or raw > self.autocal_raw_max:
                self.autocal_raw_max = raw

        if self.ticks_diff(now_ms, self.autocal_start_ms) >= self.cfg["AUTOCAL_DURATION_MS"]:
            self._finish_autocal_channel()
            current_idx = self.current_autocal_index()

        return self.cfg["AUTOCAL_SUSPEND_OUTPUT"] and current_idx == idx
