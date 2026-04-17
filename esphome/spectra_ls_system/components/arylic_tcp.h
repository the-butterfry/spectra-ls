// Description: Shared Arylic TCP transport helpers for Spectra LS System (queueing, coalescing, and send path).
// Version: 2026.04.17.3
// Last updated: 2026-04-17

#pragma once

#include "esphome.h"
#include <arpa/inet.h>
#include <lwip/sockets.h>
#include <string>
#include <vector>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <cstring>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>

namespace esphome {
namespace arylic_tcp {

#ifndef SLS_ARYLIC_TCP_TIMEOUT_MS
#define SLS_ARYLIC_TCP_TIMEOUT_MS 120
#endif

#ifndef SLS_ARYLIC_TCP_MIN_INTERVAL_MS
#define SLS_ARYLIC_TCP_MIN_INTERVAL_MS 50
#endif

#ifndef SLS_ARYLIC_TCP_DUP_SUPPRESS_MS
#define SLS_ARYLIC_TCP_DUP_SUPPRESS_MS 50
#endif

#ifndef SLS_ARYLIC_TCP_BACKOFF_MS
#define SLS_ARYLIC_TCP_BACKOFF_MS 200
#endif

#ifndef SLS_ARYLIC_TCP_BURST_GUARD_ENABLED
#define SLS_ARYLIC_TCP_BURST_GUARD_ENABLED 1
#endif

#ifndef SLS_ARYLIC_TCP_BURST_WINDOW_MS
#define SLS_ARYLIC_TCP_BURST_WINDOW_MS 180
#endif

#ifndef SLS_ARYLIC_TCP_BURST_MAX_SENDS
#define SLS_ARYLIC_TCP_BURST_MAX_SENDS 3
#endif

#ifndef SLS_ARYLIC_TCP_QUEUE_LEN
#define SLS_ARYLIC_TCP_QUEUE_LEN 16
#endif

#ifndef SLS_ARYLIC_TCP_WORKER_STACK
#define SLS_ARYLIC_TCP_WORKER_STACK 4096
#endif

#ifndef SLS_ARYLIC_TCP_WORKER_PRIO
#define SLS_ARYLIC_TCP_WORKER_PRIO 1
#endif

#ifndef SLS_ARYLIC_TCP_LOG_INTERVAL_MS
#define SLS_ARYLIC_TCP_LOG_INTERVAL_MS 500
#endif

inline void append_le_u32(std::vector<uint8_t> &out, uint32_t value) {
	out.push_back(static_cast<uint8_t>(value & 0xFF));
	out.push_back(static_cast<uint8_t>((value >> 8) & 0xFF));
	out.push_back(static_cast<uint8_t>((value >> 16) & 0xFF));
	out.push_back(static_cast<uint8_t>((value >> 24) & 0xFF));
}

inline void log_tx_throttled(const char *host, uint16_t port, const std::string &payload) {
	static uint32_t last_log_ms = 0;
	const uint32_t now = millis();
	if (now - last_log_ms < static_cast<uint32_t>(SLS_ARYLIC_TCP_LOG_INTERVAL_MS)) return;
	last_log_ms = now;
	ESP_LOGI("arylic_tcp", "TX host=%s port=%u payload=%s", host ? host : "", (unsigned) port,
					 payload.c_str());
}

inline bool send_payload(const char *host, uint16_t port, const std::string &payload, uint32_t timeout_ms);

constexpr size_t ARYLIC_TCP_HOST_LEN = 64;
constexpr size_t ARYLIC_TCP_PAYLOAD_LEN = 128;
constexpr size_t ARYLIC_TCP_QUEUE_LEN = static_cast<size_t>(SLS_ARYLIC_TCP_QUEUE_LEN);
constexpr uint32_t ARYLIC_TCP_TIMEOUT_MS = static_cast<uint32_t>(SLS_ARYLIC_TCP_TIMEOUT_MS);
constexpr uint32_t ARYLIC_TCP_MIN_INTERVAL_MS = static_cast<uint32_t>(SLS_ARYLIC_TCP_MIN_INTERVAL_MS);
constexpr uint32_t ARYLIC_TCP_DUP_SUPPRESS_MS = static_cast<uint32_t>(SLS_ARYLIC_TCP_DUP_SUPPRESS_MS);
constexpr uint32_t ARYLIC_TCP_BACKOFF_MS = static_cast<uint32_t>(SLS_ARYLIC_TCP_BACKOFF_MS);
// Reversible burst guard: set false to disable and restore previous behavior.
constexpr bool ARYLIC_TCP_BURST_GUARD_ENABLED = (SLS_ARYLIC_TCP_BURST_GUARD_ENABLED != 0);
constexpr uint32_t ARYLIC_TCP_BURST_WINDOW_MS = static_cast<uint32_t>(SLS_ARYLIC_TCP_BURST_WINDOW_MS);
constexpr uint8_t ARYLIC_TCP_BURST_MAX_SENDS = static_cast<uint8_t>(SLS_ARYLIC_TCP_BURST_MAX_SENDS);
constexpr uint32_t ARYLIC_TCP_WORKER_STACK = static_cast<uint32_t>(SLS_ARYLIC_TCP_WORKER_STACK);
constexpr UBaseType_t ARYLIC_TCP_WORKER_PRIO = static_cast<UBaseType_t>(SLS_ARYLIC_TCP_WORKER_PRIO);

struct ArylicTcpItem {
	char host[ARYLIC_TCP_HOST_LEN];
	uint16_t port;
	char payload[ARYLIC_TCP_PAYLOAD_LEN];
};

static QueueHandle_t arylic_tcp_queue = nullptr;
static TaskHandle_t arylic_tcp_task = nullptr;

struct ArylicTcpRecent {
	char host[ARYLIC_TCP_HOST_LEN];
	uint16_t port;
	uint32_t last_send_ms;
	uint32_t last_enqueue_ms;
	uint32_t burst_window_start_ms;
	uint8_t burst_send_count;
	char last_payload[ARYLIC_TCP_PAYLOAD_LEN];
	char last_sent_payload[ARYLIC_TCP_PAYLOAD_LEN];
};

static ArylicTcpRecent arylic_tcp_recent[4] = {};
static uint32_t arylic_tcp_backoff_until_ms = 0;

inline bool tcp_backoff_active() {
	if (arylic_tcp_backoff_until_ms == 0) return false;
	const uint32_t now = millis();
	return static_cast<int32_t>(arylic_tcp_backoff_until_ms - now) > 0;
}

inline void tcp_backoff_start() {
	const uint32_t now = millis();
	arylic_tcp_backoff_until_ms = now + ARYLIC_TCP_BACKOFF_MS;
}

inline uint32_t compute_burst_guard_wait_ms(ArylicTcpRecent *recent) {
	if (!ARYLIC_TCP_BURST_GUARD_ENABLED || recent == nullptr) return 0;
	const uint32_t now = millis();
	if (recent->burst_window_start_ms == 0 || now - recent->burst_window_start_ms >= ARYLIC_TCP_BURST_WINDOW_MS) {
		recent->burst_window_start_ms = now;
		recent->burst_send_count = 0;
		return 0;
	}
	if (recent->burst_send_count < ARYLIC_TCP_BURST_MAX_SENDS) return 0;
	return ARYLIC_TCP_BURST_WINDOW_MS - (now - recent->burst_window_start_ms);
}

inline void note_burst_send(ArylicTcpRecent *recent) {
	if (!ARYLIC_TCP_BURST_GUARD_ENABLED || recent == nullptr) return;
	const uint32_t now = millis();
	if (recent->burst_window_start_ms == 0 || now - recent->burst_window_start_ms >= ARYLIC_TCP_BURST_WINDOW_MS) {
		recent->burst_window_start_ms = now;
		recent->burst_send_count = 1;
		return;
	}
	if (recent->burst_send_count < 0xFF) {
		recent->burst_send_count++;
	}
}

inline ArylicTcpRecent *find_recent(const char *host, uint16_t port) {
	if (host == nullptr || host[0] == '\0') return nullptr;
	ArylicTcpRecent *empty = nullptr;
	for (auto &entry : arylic_tcp_recent) {
		if (entry.host[0] == '\0') {
			if (empty == nullptr) empty = &entry;
			continue;
		}
		if (entry.port == port && strncmp(entry.host, host, ARYLIC_TCP_HOST_LEN) == 0) {
			return &entry;
		}
	}
	if (empty != nullptr) {
		strncpy(empty->host, host, ARYLIC_TCP_HOST_LEN - 1);
		empty->host[ARYLIC_TCP_HOST_LEN - 1] = '\0';
		empty->port = port;
		empty->last_send_ms = 0;
		empty->last_enqueue_ms = 0;
		empty->burst_window_start_ms = 0;
		empty->burst_send_count = 0;
		empty->last_payload[0] = '\0';
		empty->last_sent_payload[0] = '\0';
		return empty;
	}
	return nullptr;
}

inline void arylic_tcp_worker(void *) {
	ArylicTcpItem item{};
	for (;;) {
		if (arylic_tcp_queue == nullptr) {
			vTaskDelay(pdMS_TO_TICKS(50));
			continue;
		}
		if (xQueueReceive(arylic_tcp_queue, &item, portMAX_DELAY) != pdTRUE) {
			continue;
		}
		std::string payload(item.payload);
		ArylicTcpRecent *recent = find_recent(item.host, item.port);
		if (recent != nullptr) {
			if (recent->last_payload[0] != '\0' &&
					strncmp(recent->last_payload, payload.c_str(), ARYLIC_TCP_PAYLOAD_LEN) != 0) {
				payload = recent->last_payload;
			}
			const uint32_t burst_wait_ms = compute_burst_guard_wait_ms(recent);
			if (burst_wait_ms > 0) {
				static uint32_t last_burst_log_ms = 0;
				const uint32_t now = millis();
				if (now - last_burst_log_ms >= 500) {
					last_burst_log_ms = now;
					ESP_LOGI("arylic_tcp", "burst_guard host=%s port=%u wait=%ums", item.host,
							 (unsigned) item.port, (unsigned) burst_wait_ms);
				}
				vTaskDelay(pdMS_TO_TICKS(burst_wait_ms));
			}
			if (recent->last_sent_payload[0] != '\0' &&
					strncmp(recent->last_sent_payload, payload.c_str(), ARYLIC_TCP_PAYLOAD_LEN) == 0) {
				const uint32_t now = millis();
				if (now - recent->last_send_ms < ARYLIC_TCP_MIN_INTERVAL_MS) {
					vTaskDelay(1);
					continue;
				}
			}
		}
		send_payload(item.host, item.port, payload, ARYLIC_TCP_TIMEOUT_MS);
		vTaskDelay(1);
	}
}

inline void ensure_arylic_tcp_worker() {
	if (arylic_tcp_queue == nullptr) {
		arylic_tcp_queue = xQueueCreate(ARYLIC_TCP_QUEUE_LEN, sizeof(ArylicTcpItem));
	}
	if (arylic_tcp_task == nullptr && arylic_tcp_queue != nullptr) {
		xTaskCreate(arylic_tcp_worker, "arylic_tcp", ARYLIC_TCP_WORKER_STACK, nullptr,
								ARYLIC_TCP_WORKER_PRIO, &arylic_tcp_task);
	}
}

inline bool enqueue_payload(const char *host, uint16_t port, const std::string &payload) {
	if (host == nullptr || host[0] == '\0') {
		ESP_LOGW("arylic_tcp", "host not set");
		return false;
	}
	if (payload.empty()) {
		ESP_LOGW("arylic_tcp", "payload empty");
		return false;
	}
	if (payload.size() >= ARYLIC_TCP_PAYLOAD_LEN) {
		ESP_LOGW("arylic_tcp", "payload too long len=%u", (unsigned) payload.size());
		return false;
	}
	ArylicTcpRecent *recent = find_recent(host, port);
	if (recent != nullptr && recent->last_payload[0] != '\0') {
		const uint32_t now = millis();
		if ((now - recent->last_enqueue_ms) < ARYLIC_TCP_DUP_SUPPRESS_MS &&
				strncmp(recent->last_payload, payload.c_str(), ARYLIC_TCP_PAYLOAD_LEN) == 0) {
			return true;
		}
	}

	ensure_arylic_tcp_worker();
	if (arylic_tcp_queue == nullptr) {
		ESP_LOGW("arylic_tcp", "queue not available");
		return false;
	}
	ArylicTcpItem item{};
	strncpy(item.host, host, ARYLIC_TCP_HOST_LEN - 1);
	item.host[ARYLIC_TCP_HOST_LEN - 1] = '\0';
	item.port = port;
	strncpy(item.payload, payload.c_str(), ARYLIC_TCP_PAYLOAD_LEN - 1);
	item.payload[ARYLIC_TCP_PAYLOAD_LEN - 1] = '\0';

	if (recent != nullptr) {
		recent->last_enqueue_ms = millis();
		strncpy(recent->last_payload, item.payload, ARYLIC_TCP_PAYLOAD_LEN - 1);
		recent->last_payload[ARYLIC_TCP_PAYLOAD_LEN - 1] = '\0';
	}

	if (xQueueSend(arylic_tcp_queue, &item, 0) == pdTRUE) {
		return true;
	}
	ArylicTcpItem dropped{};
	xQueueReceive(arylic_tcp_queue, &dropped, 0);
	if (xQueueSend(arylic_tcp_queue, &item, 0) == pdTRUE) {
		return true;
	}
	ESP_LOGW("arylic_tcp", "queue full (drop)");
	return false;
}

inline bool wait_writable(int sock, uint32_t timeout_ms) {
	if (timeout_ms == 0) return false;
	fd_set write_set;
	FD_ZERO(&write_set);
	FD_SET(sock, &write_set);
	timeval tv{};
	tv.tv_sec = static_cast<int>(timeout_ms / 1000);
	tv.tv_usec = static_cast<int>((timeout_ms % 1000) * 1000);
	const int res = ::select(sock + 1, nullptr, &write_set, nullptr, &tv);
	return res > 0 && FD_ISSET(sock, &write_set);
}

inline uint32_t remaining_ms(uint32_t deadline_ms) {
	const uint32_t now = millis();
	const int32_t delta = static_cast<int32_t>(deadline_ms - now);
	return delta <= 0 ? 0u : static_cast<uint32_t>(delta);
}

inline bool send_payload(const char *host, uint16_t port, const std::string &payload, uint32_t timeout_ms = ARYLIC_TCP_TIMEOUT_MS) {
	if (host == nullptr || host[0] == '\0') {
		ESP_LOGW("arylic_tcp", "host not set");
		return false;
	}
	if (tcp_backoff_active()) {
		return false;
	}

	ArylicTcpRecent *recent = find_recent(host, port);
	if (recent != nullptr) {
		const uint32_t now = millis();
		if (now - recent->last_send_ms < ARYLIC_TCP_MIN_INTERVAL_MS) {
			const uint32_t wait_ms = ARYLIC_TCP_MIN_INTERVAL_MS - (now - recent->last_send_ms);
			vTaskDelay(pdMS_TO_TICKS(wait_ms));
		}
	}

	const uint8_t header[4] = {0x18, 0x96, 0x18, 0x20};
	uint32_t checksum = 0;
	for (uint8_t b : payload) checksum += b;

	std::vector<uint8_t> packet;
	packet.reserve(4 + 4 + 4 + 8 + payload.size());
	packet.insert(packet.end(), header, header + 4);
	append_le_u32(packet, static_cast<uint32_t>(payload.size()));
	append_le_u32(packet, checksum);
	for (int i = 0; i < 8; i++) packet.push_back(0x00);
	packet.insert(packet.end(), payload.begin(), payload.end());

	log_tx_throttled(host, port, payload);

	int sock = ::socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
	if (sock < 0) {
		ESP_LOGW("arylic_tcp", "socket() failed host=%s port=%u errno=%d", host, (unsigned) port, errno);
		tcp_backoff_start();
		return false;
	}

	const uint32_t deadline_ms = millis() + timeout_ms;

	sockaddr_in dest{};
	dest.sin_family = AF_INET;
	dest.sin_port = htons(port);
	dest.sin_addr.s_addr = inet_addr(host);
	if (dest.sin_addr.s_addr == INADDR_NONE) {
		ESP_LOGW("arylic_tcp", "invalid host=%s port=%u", host, (unsigned) port);
		::close(sock);
		tcp_backoff_start();
		return false;
	}

	int flags = ::fcntl(sock, F_GETFL, 0);
	if (flags >= 0) {
		::fcntl(sock, F_SETFL, flags | O_NONBLOCK);
	}

	int conn_res = ::connect(sock, reinterpret_cast<sockaddr *>(&dest), sizeof(dest));
	if (conn_res != 0) {
		if (errno != EINPROGRESS) {
			ESP_LOGW("arylic_tcp", "connect() failed host=%s port=%u errno=%d", host, (unsigned) port, errno);
			::close(sock);
			tcp_backoff_start();
			return false;
		}
		const uint32_t wait_ms = remaining_ms(deadline_ms);
		if (!wait_writable(sock, wait_ms)) {
			ESP_LOGW("arylic_tcp", "connect() timeout host=%s port=%u", host, (unsigned) port);
			::close(sock);
			tcp_backoff_start();
			return false;
		}
		int err = 0;
		socklen_t err_len = sizeof(err);
		if (::getsockopt(sock, SOL_SOCKET, SO_ERROR, &err, &err_len) != 0 || err != 0) {
			ESP_LOGW("arylic_tcp", "connect() failed host=%s port=%u errno=%d", host, (unsigned) port, err);
			::close(sock);
			tcp_backoff_start();
			return false;
		}
	}

	size_t total_sent = 0;
	while (total_sent < packet.size()) {
		const uint32_t wait_ms = remaining_ms(deadline_ms);
		if (wait_ms == 0) {
			ESP_LOGW("arylic_tcp", "send() timeout host=%s port=%u", host, (unsigned) port);
			::shutdown(sock, SHUT_RDWR);
			::close(sock);
			tcp_backoff_start();
			return false;
		}
		if (!wait_writable(sock, wait_ms)) {
			ESP_LOGW("arylic_tcp", "send() wait timeout host=%s port=%u", host, (unsigned) port);
			::shutdown(sock, SHUT_RDWR);
			::close(sock);
			tcp_backoff_start();
			return false;
		}
		const uint8_t *data = packet.data() + total_sent;
		const size_t remaining = packet.size() - total_sent;
		const ssize_t sent = ::send(sock, data, remaining, 0);
		if (sent > 0) {
			total_sent += static_cast<size_t>(sent);
			continue;
		}
		if (sent < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
			continue;
		}
		ESP_LOGW("arylic_tcp", "send() failed host=%s port=%u errno=%d", host, (unsigned) port, errno);
		::shutdown(sock, SHUT_RDWR);
		::close(sock);
		tcp_backoff_start();
		return false;
	}

	::shutdown(sock, SHUT_RDWR);
	::close(sock);
	if (recent != nullptr) {
		recent->last_send_ms = millis();
		note_burst_send(recent);
		strncpy(recent->last_sent_payload, payload.c_str(), ARYLIC_TCP_PAYLOAD_LEN - 1);
		recent->last_sent_payload[ARYLIC_TCP_PAYLOAD_LEN - 1] = '\0';
	}
	return true;
}

inline bool send_passthrough(const char *host, uint16_t port, const std::string &uart_cmd) {
	if (uart_cmd.empty()) {
		ESP_LOGW("arylic_tcp", "passthrough cmd empty");
		return false;
	}
	std::string payload = "MCU+PAS+RAKOIT:";
	payload += uart_cmd;
	if (payload.back() != '&') payload += "&";
	return enqueue_payload(host, port, payload);
}

inline bool send_passthrough(const char *host, uint16_t port, const char *uart_cmd) {
	if (uart_cmd == nullptr) {
		ESP_LOGW("arylic_tcp", "passthrough cmd null");
		return false;
	}
	return send_passthrough(host, port, std::string(uart_cmd));
}

inline std::vector<std::string> split_hosts(const std::string &csv) {
	std::vector<std::string> hosts;
	if (csv.empty()) return hosts;
	size_t start = 0;
	while (start < csv.size()) {
		size_t end = csv.find(',', start);
		if (end == std::string::npos) end = csv.size();
		size_t tok_start = csv.find_first_not_of(" \t", start);
		size_t tok_end = csv.find_last_not_of(" \t", end > 0 ? end - 1 : end);
		if (tok_start != std::string::npos && tok_start < end && tok_end != std::string::npos && tok_end >= tok_start) {
			hosts.push_back(csv.substr(tok_start, tok_end - tok_start + 1));
		}
		start = end + 1;
	}
	return hosts;
}

inline bool send_volume(const char *host, uint16_t port, int volume) {
	if (volume < 0) volume = 0;
	if (volume > 100) volume = 100;
	char cmd[24];
	snprintf(cmd, sizeof(cmd), "VOL:%d", volume);
	return send_passthrough(host, port, cmd);
}

inline bool send_volume_multi(const std::string &hosts_csv, uint16_t port, int volume) {
	auto hosts = split_hosts(hosts_csv);
	bool ok = false;
	for (const auto &host : hosts) {
		ok = send_volume(host.c_str(), port, volume) || ok;
	}
	return ok;
}

inline bool send_mute(const char *host, uint16_t port, bool muted) {
	char cmd[16];
	snprintf(cmd, sizeof(cmd), "MUT:%d", muted ? 1 : 0);
	return send_passthrough(host, port, cmd);
}

inline bool send_mute_multi(const std::string &hosts_csv, uint16_t port, bool muted) {
	auto hosts = split_hosts(hosts_csv);
	bool ok = false;
	for (const auto &host : hosts) {
		ok = send_mute(host.c_str(), port, muted) || ok;
	}
	return ok;
}

inline bool send_play_pause(const char *host, uint16_t port) {
	return send_passthrough(host, port, "POP");
}

inline bool send_next(const char *host, uint16_t port) {
	return send_passthrough(host, port, "NXT");
}

inline bool send_prev(const char *host, uint16_t port) {
	return send_passthrough(host, port, "PRE");
}

inline bool send_source(const char *host, uint16_t port, const std::string &source) {
	if (source.empty()) {
		ESP_LOGW("arylic_tcp", "source empty");
		return false;
	}
	std::string cmd = "SRC:" + source;
	return send_passthrough(host, port, cmd);
}

inline bool send_source_multi(const std::string &hosts_csv, uint16_t port, const std::string &source) {
	auto hosts = split_hosts(hosts_csv);
	bool ok = false;
	for (const auto &host : hosts) {
		ok = send_source(host.c_str(), port, source) || ok;
	}
	return ok;
}

inline bool send_bass(const char *host, uint16_t port, int bass) {
	if (bass < -10) bass = -10;
	if (bass > 10) bass = 10;
	char cmd[24];
	snprintf(cmd, sizeof(cmd), "BAS:%d", bass);
	return send_passthrough(host, port, cmd);
}

inline bool send_bass_multi(const std::string &hosts_csv, uint16_t port, int bass) {
	auto hosts = split_hosts(hosts_csv);
	bool ok = false;
	for (const auto &host : hosts) {
		ok = send_bass(host.c_str(), port, bass) || ok;
	}
	return ok;
}

inline bool send_treble(const char *host, uint16_t port, int treble) {
	if (treble < -10) treble = -10;
	if (treble > 10) treble = 10;
	char cmd[24];
	snprintf(cmd, sizeof(cmd), "TRE:%d", treble);
	return send_passthrough(host, port, cmd);
}

inline bool send_treble_multi(const std::string &hosts_csv, uint16_t port, int treble) {
	auto hosts = split_hosts(hosts_csv);
	bool ok = false;
	for (const auto &host : hosts) {
		ok = send_treble(host.c_str(), port, treble) || ok;
	}
	return ok;
}

inline bool send_mid(const char *host, uint16_t port, int mid) {
	if (mid < -10) mid = -10;
	if (mid > 10) mid = 10;
	char cmd[24];
	snprintf(cmd, sizeof(cmd), "MID:%d", mid);
	return send_passthrough(host, port, cmd);
}

inline bool send_mid_multi(const std::string &hosts_csv, uint16_t port, int mid) {
	auto hosts = split_hosts(hosts_csv);
	bool ok = false;
	for (const auto &host : hosts) {
		ok = send_mid(host.c_str(), port, mid) || ok;
	}
	return ok;
}

}  // namespace arylic_tcp
}  // namespace esphome
