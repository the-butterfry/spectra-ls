// Description: Shared OLED text layout helpers for pixel-accurate centered wrap/fit across Spectra LS display paths.
// Version: 2026.04.18.2
// Last updated: 2026-04-18

#pragma once

#include <algorithm>
#include <cctype>
#include <string>
#include <vector>

#include "esphome/components/display/display.h"
#include "esphome/core/color.h"
#include "esphome/core/hal.h"

namespace sls_oled_text {

inline void trim_ascii(std::string &value) {
  size_t start = value.find_first_not_of(" \t\n\r");
  size_t end = value.find_last_not_of(" \t\n\r");
  if (start == std::string::npos || end == std::string::npos) {
    value.clear();
    return;
  }
  value = value.substr(start, end - start + 1);
}

inline int text_width_px(esphome::display::Display &it, esphome::font::Font *font, const std::string &text) {
  if (text.empty()) return 0;
  int x1 = 0;
  int y1 = 0;
  int tw = 0;
  int th = 0;
  it.get_text_bounds(0, 0, text.c_str(), font, esphome::display::TextAlign::TOP_LEFT, &x1, &y1, &tw, &th);
  return tw;
}

inline std::string fit_text_to_width(esphome::display::Display &it, esphome::font::Font *font,
                                     const std::string &raw, int max_width, bool add_ellipsis) {
  std::string text = raw;
  trim_ascii(text);
  if (text.empty() || max_width <= 0) return std::string("");
  if (text_width_px(it, font, text) <= max_width) return text;

  const std::string ellipsis = add_ellipsis ? std::string("...") : std::string("");
  const int ellipsis_w = ellipsis.empty() ? 0 : text_width_px(it, font, ellipsis);

  std::string out = text;
  while (!out.empty()) {
    if (!ellipsis.empty()) {
      std::string candidate = out + ellipsis;
      if (text_width_px(it, font, candidate) <= max_width) {
        trim_ascii(candidate);
        return candidate;
      }
    } else if (text_width_px(it, font, out) <= max_width) {
      trim_ascii(out);
      return out;
    }

    out.pop_back();
    trim_ascii(out);
  }

  if (!ellipsis.empty() && ellipsis_w <= max_width) return ellipsis;
  return std::string("");
}

inline std::vector<std::string> split_words(const std::string &raw) {
  std::vector<std::string> words;
  std::string token;
  for (char ch : raw) {
    if (std::isspace(static_cast<unsigned char>(ch))) {
      trim_ascii(token);
      if (!token.empty()) words.push_back(token);
      token.clear();
      continue;
    }
    token.push_back(ch);
  }
  trim_ascii(token);
  if (!token.empty()) words.push_back(token);
  return words;
}

inline std::vector<std::string> wrap_two_lines(esphome::display::Display &it, esphome::font::Font *font,
                                               const std::string &raw, int max_width, bool add_ellipsis = true) {
  std::vector<std::string> lines;
  std::string text = raw;
  trim_ascii(text);
  if (text.empty() || max_width <= 0) return lines;

  if (text_width_px(it, font, text) <= max_width) {
    lines.push_back(text);
    return lines;
  }

  const auto words = split_words(text);
  if (words.size() >= 2) {
    int best_split = -1;
    int best_max_w = 1000000;
    int best_balance = 1000000;

    for (int split = 1; split < static_cast<int>(words.size()); split++) {
      std::string l1;
      for (int i = 0; i < split; i++) {
        if (!l1.empty()) l1 += " ";
        l1 += words[i];
      }
      std::string l2;
      for (int i = split; i < static_cast<int>(words.size()); i++) {
        if (!l2.empty()) l2 += " ";
        l2 += words[i];
      }

      const int w1 = text_width_px(it, font, l1);
      const int w2 = text_width_px(it, font, l2);
      if (w1 <= max_width && w2 <= max_width) {
        const int max_w = (w1 > w2) ? w1 : w2;
        const int balance = (w1 > w2) ? (w1 - w2) : (w2 - w1);
        if (max_w < best_max_w || (max_w == best_max_w && balance < best_balance)) {
          best_max_w = max_w;
          best_balance = balance;
          best_split = split;
        }
      }
    }

    if (best_split > 0) {
      std::string l1;
      for (int i = 0; i < best_split; i++) {
        if (!l1.empty()) l1 += " ";
        l1 += words[i];
      }
      std::string l2;
      for (int i = best_split; i < static_cast<int>(words.size()); i++) {
        if (!l2.empty()) l2 += " ";
        l2 += words[i];
      }
      trim_ascii(l1);
      trim_ascii(l2);
      if (!l1.empty()) lines.push_back(l1);
      if (!l2.empty()) lines.push_back(l2);
      return lines;
    }
  }

  // Fallback for long unbreakable strings or no feasible split:
  // keep first line as max-fit prefix, second as max-fit with ellipsis.
  std::string line1;
  std::string remainder;
  for (size_t i = 1; i <= text.size(); i++) {
    std::string candidate = text.substr(0, i);
    if (text_width_px(it, font, candidate) <= max_width) {
      line1 = candidate;
      continue;
    }
    break;
  }
  trim_ascii(line1);

  if (!line1.empty() && line1.size() < text.size()) {
    remainder = text.substr(line1.size());
  } else {
    remainder = text;
  }
  trim_ascii(remainder);

  if (line1.empty()) {
    line1 = fit_text_to_width(it, font, text, max_width, add_ellipsis);
    if (!line1.empty()) lines.push_back(line1);
    return lines;
  }

  std::string line2 = fit_text_to_width(it, font, remainder, max_width, add_ellipsis);
  if (!line1.empty()) lines.push_back(line1);
  if (!line2.empty()) lines.push_back(line2);
  return lines;
}

inline bool needs_wrap_two_lines(esphome::display::Display &it, esphome::font::Font *font,
                                 const std::string &raw, int max_width) {
  auto lines = wrap_two_lines(it, font, raw, max_width, false);
  return lines.size() > 1;
}

inline void draw_center_wrapped(esphome::display::Display &it, int center_x,
                                esphome::font::Font *font, int line_h, int y, int row_h,
                                const std::string &raw, esphome::Color color, int max_width,
                                bool add_ellipsis = true) {
  auto lines = wrap_two_lines(it, font, raw, max_width, add_ellipsis);
  if (lines.empty()) return;
  if (lines.size() == 1) {
    const int y0 = y + ((row_h - line_h) / 2);
    it.printf(center_x, y0, font, color, esphome::display::TextAlign::TOP_CENTER, "%s", lines[0].c_str());
    return;
  }

  const int line_gap = 1;
  const int total_h = (line_h * 2) + line_gap;
  const int y0 = y + ((row_h - total_h) / 2);
  it.printf(center_x, y0, font, color, esphome::display::TextAlign::TOP_CENTER, "%s", lines[0].c_str());
  it.printf(center_x, y0 + line_h + line_gap, font, color, esphome::display::TextAlign::TOP_CENTER, "%s", lines[1].c_str());
}

}  // namespace sls_oled_text
