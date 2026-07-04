// Description: Shared menu navigation helpers for top-level encoder direction mapping and wrapped index movement.
// Version: 2026.06.23.1
// Last updated: 2026-06-23

#pragma once

#include <string>
#include <vector>

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

inline void trim_ascii_in_place(std::string &value) {
  size_t start = value.find_first_not_of(" \t\n\r");
  size_t end = value.find_last_not_of(" \t\n\r");
  if (start == std::string::npos || end == std::string::npos) {
    value.clear();
    return;
  }
  value = value.substr(start, end - start + 1);
}

inline std::vector<std::string> parse_options_list(const std::string &raw) {
  std::vector<std::string> out;
  if (raw.empty()) return out;

  std::string token;
  bool in_quote = false;
  char quote_char = 0;
  for (char ch : raw) {
    if (ch == '\\') continue;
    if ((ch == '\'' || ch == '"')) {
      if (!in_quote) {
        in_quote = true;
        quote_char = ch;
        continue;
      }
      if (quote_char == ch) {
        in_quote = false;
        continue;
      }
    }
    if (!in_quote && (ch == '[' || ch == ']')) continue;
    if (!in_quote && ch == ',') {
      trim_ascii_in_place(token);
      if (!token.empty()) out.push_back(token);
      token.clear();
      continue;
    }
    token.push_back(ch);
  }

  trim_ascii_in_place(token);
  if (!token.empty()) out.push_back(token);
  return out;
}

inline int parse_options_count(const std::string &raw) {
  return static_cast<int>(parse_options_list(raw).size());
}

}  // namespace sls_menu_nav
