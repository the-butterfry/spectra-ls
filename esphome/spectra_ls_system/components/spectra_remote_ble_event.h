// Description: BLE advertisement helper for Spectra remote control events (manufacturer payload lane).
// Version: 2026.07.17.6
// Last updated: 2026-07-17

#pragma once

#include <cstdint>

#include "esp_err.h"
#include "esp_gap_ble_api.h"

namespace esphome::spectra_remote_ble {

static constexpr uint16_t kCompanyId = 0x02E5;
static constexpr uint8_t kProtoVersion = 1;

static uint8_t s_seq = 0;
static bool s_gap_registered = false;

static esp_ble_adv_params_t s_adv_params = {
    .adv_int_min = 0x00A0,
    .adv_int_max = 0x00A0,
    .adv_type = ADV_TYPE_NONCONN_IND,
  .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
    .peer_addr = {0, 0, 0, 0, 0, 0},
    .peer_addr_type = BLE_ADDR_TYPE_PUBLIC,
    .channel_map = ADV_CHNL_ALL,
    .adv_filter_policy = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};

inline void gap_cb(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param) {
  switch (event) {
    case ESP_GAP_BLE_ADV_DATA_RAW_SET_COMPLETE_EVT:
      esp_ble_gap_start_advertising(&s_adv_params);
      break;
    case ESP_GAP_BLE_ADV_START_COMPLETE_EVT:
      if (param != nullptr && param->adv_start_cmpl.status != ESP_BT_STATUS_SUCCESS) {
      }
      break;
    default:
      break;
  }
}

inline bool ensure_gap_registered() {
  if (s_gap_registered) {
    return true;
  }
  const esp_err_t reg_err = esp_ble_gap_register_callback(gap_cb);
  if (reg_err != ESP_OK && reg_err != ESP_ERR_INVALID_STATE) {
    return false;
  }
  s_gap_registered = true;
  return true;
}

inline bool ensure_address_mode_ready() {
  // Public address mode requires no explicit random-address setup.
  return true;
}

inline bool emit_event(uint8_t event_code, int delta) {
  if (!ensure_gap_registered()) {
    return false;
  }
  if (!ensure_address_mode_ready()) {
    return false;
  }

  int d = delta;
  if (d > 127) d = 127;
  if (d < -127) d = -127;

  const uint8_t delta_u8 = static_cast<uint8_t>(static_cast<int8_t>(d));
  s_seq = static_cast<uint8_t>(s_seq + 1U);

  uint8_t adv_raw[16];
  size_t idx = 0;

  adv_raw[idx++] = 0x02;
  adv_raw[idx++] = 0x01;
  adv_raw[idx++] = 0x06;

  adv_raw[idx++] = 0x09;
  adv_raw[idx++] = 0xFF;
  adv_raw[idx++] = static_cast<uint8_t>(kCompanyId & 0xFF);
  adv_raw[idx++] = static_cast<uint8_t>((kCompanyId >> 8) & 0xFF);
  adv_raw[idx++] = 'S';
  adv_raw[idx++] = 'L';
  adv_raw[idx++] = kProtoVersion;
  adv_raw[idx++] = event_code;
  adv_raw[idx++] = delta_u8;
  adv_raw[idx++] = s_seq;

  (void) esp_ble_gap_stop_advertising();
  const esp_err_t cfg_err = esp_ble_gap_config_adv_data_raw(adv_raw, static_cast<uint32_t>(idx));
  return cfg_err == ESP_OK;
}

}  // namespace esphome::spectra_remote_ble
