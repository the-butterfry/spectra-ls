#pragma once

#include <cstdlib>
#include <string>

#include "esphome.h"

namespace esphome {

class ArylicUart : public Component, public uart::UARTDevice {
 public:
  explicit ArylicUart(uart::UARTComponent *parent) : UARTDevice(parent) {}

  void setup() override {
    ESP_LOGI("arylic_uart", "Arylic UART initialized");
  }

  void loop() override {
    while (available()) {
      uint8_t byte = 0;
      if (!read_byte(&byte)) {
        break;
      }
      this->consume_byte_(byte);
    }
  }

  void send_cmd(const std::string &cmd) {
    this->write_str(cmd.c_str());
  }

  void request_status() { this->send_cmd("STA;"); }

  void set_volume(int vol) {
    vol = clamp_(vol, 0, 100);
    this->send_cmd("VOL:" + std::to_string(vol) + ";");
  }

  void set_mute(bool muted) { this->send_cmd(muted ? "MUT:1;" : "MUT:0;"); }

  void set_bass(int bass) {
    bass = clamp_(bass, -10, 10);
    this->send_cmd("BAS:" + std::to_string(bass) + ";");
  }

  void set_treble(int treble) {
    treble = clamp_(treble, -10, 10);
    this->send_cmd("TRE:" + std::to_string(treble) + ";");
  }

  void set_source(const std::string &source) {
    this->send_cmd("SRC:" + source + ";");
  }

  sensor::Sensor *create_volume_sensor() {
    this->volume_sensor_ = new sensor::Sensor();
    return this->volume_sensor_;
  }

  sensor::Sensor *create_bass_sensor() {
    this->bass_sensor_ = new sensor::Sensor();
    return this->bass_sensor_;
  }

  sensor::Sensor *create_treble_sensor() {
    this->treble_sensor_ = new sensor::Sensor();
    return this->treble_sensor_;
  }

  binary_sensor::BinarySensor *create_mute_sensor() {
    this->mute_sensor_ = new binary_sensor::BinarySensor();
    return this->mute_sensor_;
  }

  binary_sensor::BinarySensor *create_playing_sensor() {
    this->playing_sensor_ = new binary_sensor::BinarySensor();
    return this->playing_sensor_;
  }

  text_sensor::TextSensor *create_source_sensor() {
    this->source_sensor_ = new text_sensor::TextSensor();
    return this->source_sensor_;
  }

  text_sensor::TextSensor *create_title_sensor() {
    this->title_sensor_ = new text_sensor::TextSensor();
    return this->title_sensor_;
  }

  text_sensor::TextSensor *create_artist_sensor() {
    this->artist_sensor_ = new text_sensor::TextSensor();
    return this->artist_sensor_;
  }

  text_sensor::TextSensor *create_album_sensor() {
    this->album_sensor_ = new text_sensor::TextSensor();
    return this->album_sensor_;
  }

 private:
  std::string line_;
  sensor::Sensor *volume_sensor_{nullptr};
  sensor::Sensor *bass_sensor_{nullptr};
  sensor::Sensor *treble_sensor_{nullptr};
  binary_sensor::BinarySensor *mute_sensor_{nullptr};
  binary_sensor::BinarySensor *playing_sensor_{nullptr};
  text_sensor::TextSensor *source_sensor_{nullptr};
  text_sensor::TextSensor *title_sensor_{nullptr};
  text_sensor::TextSensor *artist_sensor_{nullptr};
  text_sensor::TextSensor *album_sensor_{nullptr};

  void consume_byte_(uint8_t byte) {
    if (byte == ';') {
      if (!line_.empty()) {
        this->handle_line_(line_);
        line_.clear();
      }
      return;
    }

    if (line_.size() < 128) {
      line_.push_back(static_cast<char>(byte));
    } else {
      line_.clear();
    }
  }

  void handle_line_(const std::string &line) {
    if (line.rfind("STA:", 0) == 0) {
      this->parse_sta_(line.substr(4));
      return;
    }

    if (line.rfind("VOL:", 0) == 0) {
      publish_int_(volume_sensor_, line.substr(4));
      return;
    }

    if (line.rfind("MUT:", 0) == 0) {
      publish_bool_(mute_sensor_, line.substr(4) == "1");
      return;
    }

    if (line.rfind("BAS:", 0) == 0) {
      publish_int_(bass_sensor_, line.substr(4));
      return;
    }

    if (line.rfind("TRE:", 0) == 0) {
      publish_int_(treble_sensor_, line.substr(4));
      return;
    }

    if (line.rfind("SRC:", 0) == 0) {
      publish_text_(source_sensor_, line.substr(4));
      return;
    }

    if (line.rfind("TIT:", 0) == 0) {
      publish_text_(title_sensor_, decode_hex_if_needed_(line.substr(4)));
      return;
    }

    if (line.rfind("ART:", 0) == 0) {
      publish_text_(artist_sensor_, decode_hex_if_needed_(line.substr(4)));
      return;
    }

    if (line.rfind("ALB:", 0) == 0) {
      publish_text_(album_sensor_, decode_hex_if_needed_(line.substr(4)));
      return;
    }

    if (line.rfind("PLA:", 0) == 0) {
      publish_bool_(playing_sensor_, line.substr(4) == "1");
      return;
    }
  }

  void parse_sta_(const std::string &payload) {
    std::vector<std::string> parts;
    std::string token;
    for (char c : payload) {
      if (c == ',') {
        parts.push_back(token);
        token.clear();
      } else {
        token.push_back(c);
      }
    }
    parts.push_back(token);

    if (parts.size() >= 1) {
      publish_text_(source_sensor_, parts[0]);
    }
    if (parts.size() >= 2) {
      publish_bool_(mute_sensor_, parts[1] == "1");
    }
    if (parts.size() >= 3) {
      publish_int_(volume_sensor_, parts[2]);
    }
    if (parts.size() >= 4) {
      publish_int_(treble_sensor_, parts[3]);
    }
    if (parts.size() >= 5) {
      publish_int_(bass_sensor_, parts[4]);
    }
    if (parts.size() >= 8) {
      publish_bool_(playing_sensor_, parts[7] == "1");
    }
  }

  void publish_int_(sensor::Sensor *sensor, const std::string &value) {
    if (sensor == nullptr) return;
    sensor->publish_state(std::atoi(value.c_str()));
  }

  void publish_bool_(binary_sensor::BinarySensor *sensor, bool value) {
    if (sensor == nullptr) return;
    sensor->publish_state(value);
  }

  void publish_text_(text_sensor::TextSensor *sensor, const std::string &value) {
    if (sensor == nullptr) return;
    sensor->publish_state(value);
  }

  static bool is_hex_string_(const std::string &value) {
    if (value.empty() || (value.size() % 2) != 0) return false;
    for (char c : value) {
      const bool is_hex = (c >= '0' && c <= '9') ||
                          (c >= 'a' && c <= 'f') ||
                          (c >= 'A' && c <= 'F');
      if (!is_hex) return false;
    }
    return true;
  }

  static std::string decode_hex_if_needed_(const std::string &value) {
    if (!is_hex_string_(value)) return value;
    std::string out;
    out.reserve(value.size() / 2);
    for (size_t i = 0; i < value.size(); i += 2) {
      const char hi = value[i];
      const char lo = value[i + 1];
      auto nibble = [](char c) -> int {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'a' && c <= 'f') return 10 + (c - 'a');
        if (c >= 'A' && c <= 'F') return 10 + (c - 'A');
        return 0;
      };
      const char ch = (char) ((nibble(hi) << 4) | nibble(lo));
      out.push_back(ch);
    }
    return out;
  }

  static int clamp_(int value, int min_v, int max_v) {
    if (value < min_v) return min_v;
    if (value > max_v) return max_v;
    return value;
  }
};

static ArylicUart *arylic_uart = nullptr;

inline ArylicUart *get_arylic_uart(uart::UARTComponent *parent) {
  if (arylic_uart == nullptr) {
    arylic_uart = new ArylicUart(parent);
    App.register_component(arylic_uart);
  }
  return arylic_uart;
}

}  // namespace esphome
