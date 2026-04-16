#pragma once

#include "esphome.h"

inline void draw_scrolling_text(esphome::display::Display &it,
                                int x,
                                int y,
                                int line_width,
                                const std::string &text,
                                esphome::font::Font *font,
                                uint32_t now_ms,
                                uint32_t scroll_ms,
                                int char_width,
                                int scroll_gap,
                                uint32_t phase) {
  if (text.empty()) return;
  const int text_w = static_cast<int>(text.size()) * char_width;
  if (text_w <= line_width) {
    it.print(x, y, font, text.c_str());
    return;
  }
  const int cycle = text_w + scroll_gap;
  const int offset = static_cast<int>(((now_ms / scroll_ms) + phase) % cycle);
  const int start_x = x - offset;
  it.print(start_x, y, font, text.c_str());
  it.print(start_x + text_w + scroll_gap, y, font, text.c_str());
}
