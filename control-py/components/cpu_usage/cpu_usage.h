#pragma once

#include <algorithm>
#include <cstring>
#include <string>
#include <vector>

#include "esphome/core/component.h"
#include "esphome/core/log.h"
#include "esphome/components/sensor/sensor.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_timer.h"

namespace esphome {
namespace cpu_usage {

class CpuUsageSensor : public PollingComponent, public sensor::Sensor {
 public:
  explicit CpuUsageSensor(uint32_t update_ms = 10000) : PollingComponent(update_ms) {}

  void set_core0_sensor(sensor::Sensor *sensor) { core0_sensor_ = sensor; }
  void set_core1_sensor(sensor::Sensor *sensor) { core1_sensor_ = sensor; }
  void set_logging_enabled(bool enabled) { logging_enabled_ = enabled; }
  void set_log_interval_ms(uint32_t interval_ms) { log_interval_ms_ = interval_ms; }
  void set_log_tasks_enabled(bool enabled) { log_tasks_enabled_ = enabled; }
  void set_log_tasks_top(uint8_t count) { log_tasks_top_ = count; }
  void set_log_tasks_interval_ms(uint32_t interval_ms) { log_tasks_interval_ms_ = interval_ms; }

  void setup() override {
    ESP_LOGI("cpu_usage", "setup logging=%d interval=%ums", logging_enabled_ ? 1 : 0,
             (unsigned) log_interval_ms_);
  }

  void update() override {
    static bool warned_unavailable = false;
#if !defined(configGENERATE_RUN_TIME_STATS) || (configGENERATE_RUN_TIME_STATS == 0)
    if (!warned_unavailable) {
      warned_unavailable = true;
      ESP_LOGW("cpu_usage", "configGENERATE_RUN_TIME_STATS is disabled; runtime stats will be 0");
    }
    return;
#endif
    UBaseType_t task_count = uxTaskGetNumberOfTasks();
    if (task_count == 0) return;

    std::vector<TaskStatus_t> statuses;
    configRUN_TIME_COUNTER_TYPE total_runtime = 0;
    UBaseType_t got = 0;

    // Tasks can be created between count and snapshot. Retry once with padding.
    for (int attempt = 0; attempt < 2; attempt++) {
      const UBaseType_t size = (task_count > 0) ? (task_count + 4) : 8;
      statuses.assign(size, TaskStatus_t{});
      total_runtime = 0;
      got = uxTaskGetSystemState(statuses.data(), size, &total_runtime);
      if (got > 0) break;
      task_count = uxTaskGetNumberOfTasks();
    }
    if (got == 0 || total_runtime == 0) {
      if (got > 0 && total_runtime == 0) {
        for (UBaseType_t i = 0; i < got; i++) {
          total_runtime += statuses[i].ulRunTimeCounter;
        }
      }
      if (!warned_unavailable) {
        warned_unavailable = true;
        ESP_LOGW("cpu_usage", "runtime stats unavailable (got=%u total=%llu); check sdkconfig options",
                 (unsigned) got, static_cast<unsigned long long>(total_runtime));
      }
      return;
    }

    configRUN_TIME_COUNTER_TYPE idle_runtime = 0;
    configRUN_TIME_COUNTER_TYPE idle0_runtime = 0;
    configRUN_TIME_COUNTER_TYPE idle1_runtime = 0;

    for (UBaseType_t i = 0; i < got; i++) {
      const char *name = statuses[i].pcTaskName;
      if (name == nullptr) continue;
      if (std::strncmp(name, "IDLE0", 5) == 0) {
        idle0_runtime += statuses[i].ulRunTimeCounter;
        idle_runtime += statuses[i].ulRunTimeCounter;
      } else if (std::strncmp(name, "IDLE1", 5) == 0) {
        idle1_runtime += statuses[i].ulRunTimeCounter;
        idle_runtime += statuses[i].ulRunTimeCounter;
      } else if (std::strncmp(name, "IDLE", 4) == 0) {
        idle_runtime += statuses[i].ulRunTimeCounter;
      }
    }

    if (last_total_runtime_ == 0) {
      last_total_runtime_ = total_runtime;
      last_idle_runtime_ = idle_runtime;
      last_idle0_runtime_ = idle0_runtime;
      last_idle1_runtime_ = idle1_runtime;
      return;
    }

    if (total_runtime < last_total_runtime_) {
      last_total_runtime_ = total_runtime;
      last_idle_runtime_ = idle_runtime;
      last_idle0_runtime_ = idle0_runtime;
      last_idle1_runtime_ = idle1_runtime;
      return;
    }

    const configRUN_TIME_COUNTER_TYPE delta_total = total_runtime - last_total_runtime_;
    const configRUN_TIME_COUNTER_TYPE delta_idle =
        (idle_runtime >= last_idle_runtime_) ? (idle_runtime - last_idle_runtime_) : 0;
    const uint64_t now_us = esp_timer_get_time();
    if (now_us == 0 || last_sample_us_ == 0) {
      last_sample_us_ = now_us;
      last_total_runtime_ = total_runtime;
      last_idle_runtime_ = idle_runtime;
      last_idle0_runtime_ = idle0_runtime;
      last_idle1_runtime_ = idle1_runtime;
      return;
    }
    const uint64_t elapsed_us = now_us - last_sample_us_;
    if (elapsed_us == 0 || delta_total == 0) {
      if (!warned_unavailable) {
        warned_unavailable = true;
        ESP_LOGW("cpu_usage", "runtime stats delta is 0; check sdkconfig options");
      }
      return;
    }

    const uint32_t cores = portNUM_PROCESSORS > 0 ? portNUM_PROCESSORS : 1;
    const double total_per_core = static_cast<double>(elapsed_us);

    auto clamp_pct = [](float v) {
      if (v < 0.0f) v = 0.0f;
      if (v > 100.0f) v = 100.0f;
      return v;
    };

    const double total_window = static_cast<double>(elapsed_us) * static_cast<double>(cores);
    float idle_pct = static_cast<float>((static_cast<double>(delta_idle) * 100.0) / total_window);
    float cpu_pct = 100.0f - idle_pct;
    this->publish_state(clamp_pct(cpu_pct));

    if (core0_sensor_ != nullptr && total_per_core > 0.0f) {
      configRUN_TIME_COUNTER_TYPE idle0 =
          (idle0_runtime >= last_idle0_runtime_) ? (idle0_runtime - last_idle0_runtime_) : 0;
      if (idle0 == 0 && delta_idle > 0 && cores >= 1) idle0 = delta_idle / cores;
      float idle_pct0 = static_cast<float>((static_cast<double>(idle0) * 100.0) / total_per_core);
      float cpu_pct0 = 100.0f - idle_pct0;
      core0_sensor_->publish_state(clamp_pct(cpu_pct0));
    }

    if (core1_sensor_ != nullptr && total_per_core > 0.0f) {
      configRUN_TIME_COUNTER_TYPE idle1 =
          (idle1_runtime >= last_idle1_runtime_) ? (idle1_runtime - last_idle1_runtime_) : 0;
      if (idle1 == 0 && delta_idle > 0 && cores >= 2) idle1 = delta_idle / cores;
      float idle_pct1 = static_cast<float>((static_cast<double>(idle1) * 100.0) / total_per_core);
      float cpu_pct1 = 100.0f - idle_pct1;
      core1_sensor_->publish_state(clamp_pct(cpu_pct1));
    }

    if (logging_enabled_) {
      const uint32_t now = millis();
      if (log_interval_ms_ == 0 || (now - last_log_ms_) >= log_interval_ms_) {
        last_log_ms_ = now;
        ESP_LOGI("cpu_usage", "CPU=%.1f%% (idle=%.1f%%)", clamp_pct(cpu_pct), clamp_pct(idle_pct));
        if (core0_sensor_ != nullptr && total_per_core > 0.0f) {
          configRUN_TIME_COUNTER_TYPE idle0 =
              (idle0_runtime >= last_idle0_runtime_) ? (idle0_runtime - last_idle0_runtime_) : 0;
          if (idle0 == 0 && delta_idle > 0 && cores >= 1) idle0 = delta_idle / cores;
          float idle_pct0 = static_cast<float>((static_cast<double>(idle0) * 100.0) / total_per_core);
          float cpu_pct0 = 100.0f - idle_pct0;
          ESP_LOGI("cpu_usage", "CPU0=%.1f%% (idle=%.1f%%)", clamp_pct(cpu_pct0), clamp_pct(idle_pct0));
        }
        if (core1_sensor_ != nullptr && total_per_core > 0.0f) {
          configRUN_TIME_COUNTER_TYPE idle1 =
              (idle1_runtime >= last_idle1_runtime_) ? (idle1_runtime - last_idle1_runtime_) : 0;
          if (idle1 == 0 && delta_idle > 0 && cores >= 2) idle1 = delta_idle / cores;
          float idle_pct1 = static_cast<float>((static_cast<double>(idle1) * 100.0) / total_per_core);
          float cpu_pct1 = 100.0f - idle_pct1;
          ESP_LOGI("cpu_usage", "CPU1=%.1f%% (idle=%.1f%%)", clamp_pct(cpu_pct1), clamp_pct(idle_pct1));
        }
      }
    }

    if (log_tasks_enabled_) {
      const uint32_t now_ms = millis();
      if (log_tasks_interval_ms_ == 0 || (now_ms - last_log_tasks_ms_) >= log_tasks_interval_ms_) {
        last_log_tasks_ms_ = now_ms;
        const double total_window = static_cast<double>(elapsed_us) * static_cast<double>(cores);
        if (total_window > 0.0) {
          struct TaskDelta {
            std::string name;
            double pct;
          };
          std::vector<TaskDelta> deltas;
          deltas.reserve(got);

          auto find_last = [&](const char *name) -> const TaskSnapshot * {
            if (name == nullptr) return nullptr;
            for (const auto &snap : last_task_counters_) {
              if (snap.name == name) return &snap;
            }
            return nullptr;
          };

          std::vector<TaskSnapshot> next_snapshots;
          next_snapshots.reserve(got);

          for (UBaseType_t i = 0; i < got; i++) {
            const char *name = statuses[i].pcTaskName;
            if (name == nullptr) continue;
            const std::string task_name = name;
            next_snapshots.push_back({task_name, statuses[i].ulRunTimeCounter});

            if (std::strncmp(name, "IDLE", 4) == 0) continue;
            const TaskSnapshot *prev = find_last(name);
            if (prev == nullptr) continue;
            configRUN_TIME_COUNTER_TYPE delta = 0;
            if (statuses[i].ulRunTimeCounter >= prev->counter) {
              delta = statuses[i].ulRunTimeCounter - prev->counter;
            }
            if (delta == 0) continue;
            const double pct = (static_cast<double>(delta) * 100.0) / total_window;
            if (pct <= 0.01) continue;
            deltas.push_back({task_name, pct});
          }

          last_task_counters_ = std::move(next_snapshots);

          if (!deltas.empty()) {
            std::sort(deltas.begin(), deltas.end(), [](const TaskDelta &a, const TaskDelta &b) {
              return a.pct > b.pct;
            });
            const size_t limit = std::min<size_t>(log_tasks_top_, deltas.size());
            ESP_LOGI("cpu_usage", "Top tasks (%u):", (unsigned) limit);
            for (size_t i = 0; i < limit; i++) {
              ESP_LOGI("cpu_usage", "  %s: %.2f%%", deltas[i].name.c_str(), deltas[i].pct);
            }
          }
        }
      }
    } else {
      last_task_counters_.clear();
    }

    last_sample_us_ = now_us;
    last_total_runtime_ = total_runtime;
    last_idle_runtime_ = idle_runtime;
    last_idle0_runtime_ = idle0_runtime;
    last_idle1_runtime_ = idle1_runtime;
  }

 protected:
  sensor::Sensor *core0_sensor_{nullptr};
  sensor::Sensor *core1_sensor_{nullptr};
  bool logging_enabled_{false};
  uint32_t log_interval_ms_{5000};
  uint32_t last_log_ms_{0};
  configRUN_TIME_COUNTER_TYPE last_total_runtime_{0};
  configRUN_TIME_COUNTER_TYPE last_idle_runtime_{0};
  configRUN_TIME_COUNTER_TYPE last_idle0_runtime_{0};
  configRUN_TIME_COUNTER_TYPE last_idle1_runtime_{0};
  uint64_t last_sample_us_{0};
  struct TaskSnapshot {
    std::string name;
    configRUN_TIME_COUNTER_TYPE counter;
  };
  std::vector<TaskSnapshot> last_task_counters_{};
  bool log_tasks_enabled_{false};
  uint8_t log_tasks_top_{5};
  uint32_t log_tasks_interval_ms_{10000};
  uint32_t last_log_tasks_ms_{0};
};

}  // namespace cpu_usage
}  // namespace esphome
