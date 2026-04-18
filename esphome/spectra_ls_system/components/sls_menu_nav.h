// Description: Shared menu navigation helpers for top-level encoder direction mapping and wrapped index movement.
// Version: 2026.04.18.1
// Last updated: 2026-04-18

#pragma once

namespace sls_menu_nav {

inline int direction_sign(int configured_sign) {
  return configured_sign < 0 ? -1 : 1;
}

inline int normalize_encoder_delta(int raw_delta, int configured_sign) {
  if (raw_delta == 0) return 0;
  return raw_delta * direction_sign(configured_sign);
}

inline int wrap_index(int idx, int count) {
  if (count <= 0) return 0;
  while (idx < 0) idx += count;
  while (idx >= count) idx -= count;
  return idx;
}

inline int step_index(int current_idx, int step, int count) {
  return wrap_index(current_idx + step, count);
}

}  // namespace sls_menu_nav
