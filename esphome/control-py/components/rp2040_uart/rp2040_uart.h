#pragma once

#include <map>

#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

namespace esphome {
namespace rp2040_uart {

class Rp2040UartHub : public Component, public uart::UARTDevice {
 public:
	explicit Rp2040UartHub(uart::UARTComponent *parent) : UARTDevice(parent) {}

	void setup() override { ESP_LOGI("rp2040_uart", "RP2040 UART hub initialized"); }

	void dump_config() override { ESP_LOGCONFIG("rp2040_uart", "RP2040 UART Hub"); }

	void loop() override {
		while (available()) {
			uint8_t byte = 0;
			if (!read_byte(&byte)) {
				break;
			}
			this->rx_bytes_++;
			this->consume_byte_(byte);
		}

		const uint32_t now = millis();
		if (!this->warned_no_packets_ && now > 5000 && this->rx_packets_ == 0) {
			this->warned_no_packets_ = true;
			ESP_LOGW("rp2040_uart", "No packets received yet (check wiring/baud/pins)");
		}
		if (now - this->last_report_ms_ >= 15000) {
			this->last_report_ms_ = now;
			ESP_LOGD("rp2040_uart", "stats bytes=%u packets=%u last_packet_ms=%u", this->rx_bytes_,
							 this->rx_packets_, this->last_packet_ms_);
		}
	}

	void set_button_sensor(uint8_t id, binary_sensor::BinarySensor *sensor) {
		this->button_sensors_[id] = sensor;
	}

	void set_analog_sensor(uint8_t id, sensor::Sensor *sensor) { this->analog_sensors_[id] = sensor; }

	void set_encoder_sensor(uint8_t id, sensor::Sensor *sensor) { this->encoder_sensors_[id] = sensor; }

 private:
	uint8_t buffer_[10] = {0};
	uint8_t index_ = 0;
	std::map<uint8_t, binary_sensor::BinarySensor *> button_sensors_;
	std::map<uint8_t, sensor::Sensor *> analog_sensors_;
	std::map<uint8_t, sensor::Sensor *> encoder_sensors_;
	uint32_t rx_bytes_ = 0;
	uint32_t rx_packets_ = 0;
	uint32_t last_packet_ms_ = 0;
	uint32_t last_report_ms_ = 0;
	uint32_t last_dbg_log_ms_ = 0;
	bool warned_no_packets_ = false;

	void consume_byte_(uint8_t byte) {
		if (index_ == 0) {
			if (byte == 0xAA) {
				buffer_[index_++] = byte;
			}
			return;
		}

		if (index_ == 1) {
			if (byte == 0x55) {
				buffer_[index_++] = byte;
			} else {
				index_ = (byte == 0xAA) ? 1 : 0;
				buffer_[0] = 0xAA;
			}
			return;
		}

		buffer_[index_++] = byte;
		if (index_ >= 10) {
			this->handle_packet_();
			index_ = 0;
		}
	}

	void handle_packet_() {
		const uint8_t type = buffer_[2];
		const uint8_t id = buffer_[3];
		const uint32_t ts = (static_cast<uint32_t>(buffer_[4]) << 24) |
												(static_cast<uint32_t>(buffer_[5]) << 16) |
												(static_cast<uint32_t>(buffer_[6]) << 8) |
												static_cast<uint32_t>(buffer_[7]);
		const uint16_t raw_value = (static_cast<uint16_t>(buffer_[8]) << 8) |
															 static_cast<uint16_t>(buffer_[9]);

		this->rx_packets_++;
		this->last_packet_ms_ = millis();

		switch (type) {
			case 0x01: {  // button
				const bool pressed = raw_value != 0;
				auto it = button_sensors_.find(id);
				if (it != button_sensors_.end()) {
					it->second->publish_state(pressed);
				}
				ESP_LOGD("rp2040_uart", "btn id=%u val=%u ts=%u", id, pressed ? 1 : 0, ts);
				break;
			}
			case 0x02: {  // analog
				auto it = analog_sensors_.find(id);
				if (it != analog_sensors_.end()) {
					it->second->publish_state(raw_value);
				}
				ESP_LOGD("rp2040_uart", "analog id=%u val=%u ts=%u", id, raw_value, ts);
				break;
			}
			case 0x03: {  // encoder delta
				const int16_t delta = static_cast<int16_t>(raw_value);
				auto it = encoder_sensors_.find(id);
				if (it != encoder_sensors_.end()) {
					it->second->publish_state(delta);
				}
				ESP_LOGD("rp2040_uart", "enc id=%u delta=%d ts=%u", id, delta, ts);
				break;
			}
			case 0xF0: {  // debug
				const uint32_t now = millis();
				if (now - this->last_dbg_log_ms_ >= 10000) {
					this->last_dbg_log_ms_ = now;
					ESP_LOGD("rp2040_uart", "dbg id=%u val=%u ts=%u", id, raw_value, ts);
				}
				break;
			}
			default:
				ESP_LOGW("rp2040_uart", "unknown type=%u id=%u raw=%u ts=%u", type, id, raw_value, ts);
				break;
		}
	}
};

}  // namespace rp2040_uart
}  // namespace esphome
