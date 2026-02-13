#include "network_sender.h"
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <iostream>
#include <vector>

NetworkSender::NetworkSender(const Config& config)
    : config_(config), sockfd_(-1), connected_(false) {
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

    // 发送数据大小（4字节）
    uint32_t data_size = buffer.size();
    uint32_t net_size = htonl(data_size);

    if (send(sockfd_, &net_size, sizeof(net_size), 0) != sizeof(net_size)) {
        std::cerr << "发送数据大小失败" << std::endl;
        connected_ = false;
        return false;
    }

    // 发送图像数据
    size_t total_sent = 0;
    while (total_sent < data_size) {
        ssize_t sent = send(sockfd_, buffer.data() + total_sent, data_size - total_sent, 0);
        if (sent <= 0) {
            std::cerr << "发送图像数据失败" << std::endl;
            connected_ = false;
            return false;
        }
        total_sent += sent;
    }

    std::cout << "成功发送图像，大小: " << data_size << " 字节" << std::endl;
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
    if (sockfd_ >= 0) {
        close(sockfd_);
        sockfd_ = -1;
    }
    connected_ = false;
}
