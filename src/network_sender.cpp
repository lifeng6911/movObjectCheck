#include "network_sender.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <vector>

NetworkSender::NetworkSender(const Config& config)
    : config_(config), sockfd_(-1), connected_(false), running_(false) {
}

NetworkSender::~NetworkSender() {
    disconnect();
}

bool NetworkSender::connect() {
    sockfd_ = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd_ < 0) {
        std::cerr << "创建socket失败" << std::endl;
        return false;
    }

    // 设置超时
    struct timeval timeout;
    timeout.tv_sec = config_.connection_timeout / 1000;
    timeout.tv_usec = (config_.connection_timeout % 1000) * 1000;
    setsockopt(sockfd_, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(sockfd_, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    // 设置TCP保活
    int keepalive = 1;
    int keepidle = 60;
    int keepinterval = 10;
    int keepcount = 3;
    setsockopt(sockfd_, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive));
    setsockopt(sockfd_, IPPROTO_TCP, TCP_KEEPIDLE, &keepidle, sizeof(keepidle));
    setsockopt(sockfd_, IPPROTO_TCP, TCP_KEEPINTVL, &keepinterval, sizeof(keepinterval));
    setsockopt(sockfd_, IPPROTO_TCP, TCP_KEEPCNT, &keepcount, sizeof(keepcount));

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(config_.server_port);

    if (inet_pton(AF_INET, config_.server_ip.c_str(), &server_addr.sin_addr) <= 0) {
        std::cerr << "无效的服务器地址" << std::endl;
        close(sockfd_);
        return false;
    }

    if (::connect(sockfd_, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "连接服务器失败: " << config_.server_ip << ":" << config_.server_port << std::endl;
        close(sockfd_);
        return false;
    }

    connected_ = true;
    std::cout << "成功连接到服务器: " << config_.server_ip << ":" << config_.server_port << std::endl;

    // 注册设备
    if (!registerDevice()) {
        std::cerr << "设备注册失败" << std::endl;
        disconnect();
        return false;
    }

    // 启动心跳线程
    running_ = true;
    heartbeat_thread_ = std::thread(&NetworkSender::heartbeatThread, this);

    return true;
}

bool NetworkSender::registerDevice() {
    RegisterMessage msg;
    memset(&msg, 0, sizeof(msg));

    msg.header.type = MSG_REGISTER;
    msg.header.device_id = htons(config_.device_id);
    msg.header.data_length = htonl(sizeof(msg) - sizeof(MessageHeader));

    strncpy(msg.device_name, config_.device_name.c_str(), sizeof(msg.device_name) - 1);
    strncpy(msg.location, config_.device_location.c_str(), sizeof(msg.location) - 1);

    if (!sendMessage(msg.header, msg.device_name)) {
        return false;
    }

    if (!receiveAck(MSG_REGISTER_ACK)) {
        return false;
    }

    std::cout << "设备注册成功 [ID: " << config_.device_id << ", 名称: "
              << config_.device_name << "]" << std::endl;
    return true;
}

bool NetworkSender::sendHeartbeat() {
    if (!connected_) {
        return false;
    }

    MessageHeader header;
    header.type = MSG_HEARTBEAT;
    header.reserved = 0;
    header.device_id = htons(config_.device_id);
    header.data_length = 0;

    if (!sendMessage(header)) {
        std::cerr << "发送心跳失败" << std::endl;
        connected_ = false;
        return false;
    }

    // 等待心跳响应
    if (!receiveAck(MSG_HEARTBEAT_ACK)) {
        std::cerr << "心跳响应超时" << std::endl;
        connected_ = false;
        return false;
    }

    last_heartbeat_ = std::chrono::steady_clock::now();
    return true;
}

void NetworkSender::heartbeatThread() {
    std::cout << "心跳线程启动，间隔: " << config_.heartbeat_interval << "秒" << std::endl;

    while (running_) {
        if (connected_) {
            if (!sendHeartbeat()) {
                std::cerr << "心跳失败，尝试重新连接..." << std::endl;
                reconnect();
            }
        }

        // 等待下一次心跳
        for (int i = 0; i < config_.heartbeat_interval && running_; i++) {
            sleep(1);
        }
    }

    std::cout << "心跳线程退出" << std::endl;
}

bool NetworkSender::sendMessage(const MessageHeader& header, const void* data) {
    // 发送消息头
    if (send(sockfd_, &header, sizeof(header), 0) != sizeof(header)) {
        return false;
    }

    // 发送数据（如果有）
    if (data && ntohl(header.data_length) > 0) {
        uint32_t data_len = ntohl(header.data_length);
        if (send(sockfd_, data, data_len, 0) != (ssize_t)data_len) {
            return false;
        }
    }

    return true;
}

bool NetworkSender::receiveAck(MessageType expected_type) {
    MessageHeader ack_header;

    ssize_t received = recv(sockfd_, &ack_header, sizeof(ack_header), 0);
    if (received != sizeof(ack_header)) {
        return false;
    }

    if (ack_header.type != expected_type) {
        std::cerr << "收到意外的消息类型: " << (int)ack_header.type << std::endl;
        return false;
    }

    return true;
}

bool NetworkSender::sendFrame(const cv::Mat& frame) {
    if (!connected_) {
        if (!reconnect()) {
            return false;
        }
    }

    // 压缩图像为JPEG格式
    std::vector<uchar> buffer;
    std::vector<int> params = {cv::IMWRITE_JPEG_QUALITY, config_.jpeg_quality};

    if (!cv::imencode(".jpg", frame, buffer, params)) {
        std::cerr << "图像编码失败" << std::endl;
        return false;
    }

    // 构造消息头
    MessageHeader header;
    header.type = MSG_IMAGE_DATA;
    header.reserved = 0;
    header.device_id = htons(config_.device_id);
    header.data_length = htonl(buffer.size());

    // 发送消息头
    if (send(sockfd_, &header, sizeof(header), 0) != sizeof(header)) {
        std::cerr << "发送消息头失败" << std::endl;
        connected_ = false;
        return false;
    }

    // 发送图像数据
    size_t total_sent = 0;
    while (total_sent < buffer.size()) {
        ssize_t sent = send(sockfd_, buffer.data() + total_sent, buffer.size() - total_sent, 0);
        if (sent <= 0) {
            std::cerr << "发送图像数据失败" << std::endl;
            connected_ = false;
            return false;
        }
        total_sent += sent;
    }

    std::cout << "成功发送图像，大小: " << buffer.size() << " 字节" << std::endl;
    return true;
}

bool NetworkSender::reconnect() {
    disconnect();

    for (int i = 0; i < config_.max_retry; i++) {
        std::cout << "尝试重新连接... (" << (i + 1) << "/" << config_.max_retry << ")" << std::endl;
        if (connect()) {
            return true;
        }
        sleep(2);
    }

    return false;
}

void NetworkSender::disconnect() {
    running_ = false;

    // 等待心跳线程退出
    if (heartbeat_thread_.joinable()) {
        heartbeat_thread_.join();
    }

    if (sockfd_ >= 0) {
        close(sockfd_);
        sockfd_ = -1;
    }
    connected_ = false;
}
