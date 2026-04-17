# Description: Runtime autocalibration/tracking state manager for Spectra LS RP2040 firmware.
# Version: 2026.04.17.1
# Last updated: 2026-04-17
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
        self.tracking_active = False

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
            if self.calibration_missing(self.calibration, name):
                self.tracking_indices.append(idx)
        self.tracking_active = bool(self.tracking_indices)
        if self.tracking_active and self.debug_calibration_serial:
            names_line = ", ".join(self._name(idx) for idx in self.tracking_indices)
            print(f"Calibration tracking enabled for: {names_line}")

    def update_calibration_tracking(self, idx, raw):
        if not self.tracking_active or idx not in self.tracking_indices:
            return
        now = self.ticks_ms()
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
        if span < self.cfg["CALIBRATION_TRACKING_MIN_RANGE"]:
            return

        edge_span = max(1, int(span * self.cfg["CALIBRATION_TRACKING_EDGE_PCT"] / 100))
        if raw <= (min_val + edge_span):
            self.tracking_low_hits[idx] = self.tracking_low_hits.get(idx, 0) + 1
        if raw >= (max_val - edge_span):
            self.tracking_high_hits[idx] = self.tracking_high_hits.get(idx, 0) + 1

        if self.tracking_low_hits.get(idx, 0) < self.cfg["CALIBRATION_TRACKING_EDGE_MIN_SAMPLES"]:
            return
        if self.tracking_high_hits.get(idx, 0) < self.cfg["CALIBRATION_TRACKING_EDGE_MIN_SAMPLES"]:
            return

        if self.ticks_diff(now, self.tracking_min_ms.get(idx, now)) < self.cfg["CALIBRATION_TRACKING_SETTLE_MS"]:
            return
        if self.ticks_diff(now, self.tracking_max_ms.get(idx, now)) < self.cfg["CALIBRATION_TRACKING_SETTLE_MS"]:
            return

        name = self._name(idx)
        source = self._source(idx)
        self.calibration.setdefault(source, {})
        self.calibration[source][name] = {"min": int(min_val), "max": int(max_val)}
        saved = self._save_calibration()
        if saved:
            print(f"Calibration saved: {name} min={int(min_val)} max={int(max_val)}")
        else:
            print(f"Calibration NOT saved (USB mounted): {name} min={int(min_val)} max={int(max_val)}")
        if self.debug_calibration_serial:
            print(f"Calibration tracking saved: {name} min={int(min_val)} max={int(max_val)}")

        self.tracking_indices.remove(idx)
        self.tracking_active = bool(self.tracking_indices)

    def get_tracking_calibration(self, idx):
        if not self.cfg["CALIBRATION_TRACKING_DYNAMIC"]:
            return None
        min_val = self.tracking_min.get(idx)
        max_val = self.tracking_max.get(idx)
        if min_val is None or max_val is None:
            return None
        if (max_val - min_val) < self.cfg["CALIBRATION_TRACKING_MIN_RANGE"]:
            return None
        if self.tracking_low_hits.get(idx, 0) < self.cfg["CALIBRATION_TRACKING_EDGE_MIN_SAMPLES"]:
            return None
        if self.tracking_high_hits.get(idx, 0) < self.cfg["CALIBRATION_TRACKING_EDGE_MIN_SAMPLES"]:
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
