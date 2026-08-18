# Description: Now-playing candidate selection policy helpers extracted from metadata-stack orchestration.
# Version: 2026.08.18.1
# Last updated: 2026-08-18
# PARITY DIRECTIVE (until full cutover): behavior/contract edits here require same-slice two-track parity review
# and version-metadata review in runtime (`packages/` + `esphome/`) and component (`custom_components/spectra_ls/`) tracks.

from __future__ import annotations

from typing import Any


def pick_now_playing_candidate(
    *,
    eligible_rows: list[dict[str, Any]],
    passthrough_source_detected: bool,
    source_rank: dict[str, int],
) -> dict[str, Any] | None:
    """Pick best now-playing candidate row using deterministic policy ranking."""
    if len(eligible_rows) == 0:
        return None

    def _rank_tuple(row: dict[str, Any]) -> tuple[Any, ...]:
        entity_id = str(row.get("entity", "") or "")
        source = str(row.get("source", "") or "")
        pool_rank = int(row.get("pool_rank", 99) or 99)
        fresh_rank = 0 if bool(row.get("fresh", False)) else 1
        track_identity_rank = 0 if bool(row.get("has_track_identity_meta", False)) else 1
        has_meta_rank = 0 if bool(row.get("has_meta", False)) else 1
        recent_rank = 0 if bool(row.get("recent_play_progress", False)) else 1
        ma_rank = 0 if bool(row.get("ma_hint", False)) else 1
        mirror_rank = 1 if bool(row.get("transport_mirror", False)) else 0
        richness_rank = -int(row.get("meta_richness", 0) or 0)
        src_rank = int(source_rank.get(source, 50))
        return (
            pool_rank,
            fresh_rank,
            track_identity_rank,
            has_meta_rank,
            recent_rank,
            ma_rank,
            mirror_rank,
            richness_rank,
            src_rank,
            entity_id,
        )

    best_row = sorted(eligible_rows, key=_rank_tuple)[0]
    if passthrough_source_detected and not bool(best_row.get("has_track_identity_meta", False)):
        track_rows = [
            row
            for row in eligible_rows
            if bool(row.get("has_track_identity_meta", False))
            and str(row.get("state", "") or "") in {"playing", "paused", "buffering"}
        ]
        if len(track_rows) > 0:
            best_row = sorted(track_rows, key=_rank_tuple)[0]
            best_row = {
                **best_row,
                "source": "passthrough_track_identity_preferred",
            }

    return best_row
