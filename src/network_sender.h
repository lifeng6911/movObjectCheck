#ifndef NETWORK_SENDER_H
#define NETWORK_SENDER_H

#include <opencv2/opencv.hpp>
#include <string>
#include "config.h"

class NetworkSender {
public:
    NetworkSender(const Config& config);
    ~NetworkSender();

    bool connect();
    bool sendFrame(const cv::Mat& frame);
    void disconnect();

private:
    bool reconnect();

    Config config_;
    int sockfd_;
    bool connected_;
};

#endif // NETWORK_SENDER_H
