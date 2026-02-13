#ifndef NETWORK_SENDER_H
#define NETWORK_SENDER_H

#include <opencv2/opencv.hpp>
#include <string>
#include <thread>
#include <atomic>
#include <chrono>
#include "config.h"
#include "protocol.h"

class NetworkSender {
public:
    NetworkSender(const Config& config);
    ~NetworkSender();

    bool connect();
    bool sendFrame(const cv::Mat& frame);
    void disconnect();
    bool isConnected() const { return connected_; }

private:
    bool reconnect();
    bool registerDevice();
    bool sendHeartbeat();
    void heartbeatThread();
    bool sendMessage(const MessageHeader& header, const void* data = nullptr);
    bool receiveAck(MessageType expected_type);

    Config config_;
    int sockfd_;
    std::atomic<bool> connected_;
    std::atomic<bool> running_;
    std::thread heartbeat_thread_;
    std::chrono::steady_clock::time_point last_heartbeat_;
};

#endif // NETWORK_SENDER_H
