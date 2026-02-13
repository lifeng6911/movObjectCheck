#include <iostream>
#include <signal.h>
#include <unistd.h>
#include "motion_detector.h"
#include "network_sender.h"
#include "config.h"

volatile sig_atomic_t running = 1;

void signal_handler(int signum) {
    std::cout << "\n接收到信号 " << signum << "，正在退出..." << std::endl;
    running = 0;
}

int main(int argc, char* argv[]) {
    std::cout << "=== 移动物体检测系统 ===" << std::endl;

    // 注册信号处理
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    // 加载配置
    Config config;
    std::string config_file = "config/config.ini";

    if (argc > 1) {
        config_file = argv[1];
    }

    if (!config.loadFromFile(config_file)) {
        std::cout << "使用默认配置" << std::endl;
    }

    // 初始化运动检测器
    MotionDetector detector(config);
    if (!detector.initialize()) {
        std::cerr << "运动检测器初始化失败" << std::endl;
        return 1;
    }

    // 初始化网络发送器
    NetworkSender sender(config);
    if (!sender.connect()) {
        std::cerr << "警告: 无法连接到服务器，将继续尝试..." << std::endl;
    }

    std::cout << "系统启动成功，开始监控..." << std::endl;

    int no_motion_count = 0;
    const int NO_MOTION_THRESHOLD = 10;

    while (running) {
        cv::Mat frame;
        bool motion = detector.detectMotion(frame);

        if (motion) {
            std::cout << "检测到移动物体！" << std::endl;

            // 发送图像到服务器
            if (!sender.sendFrame(frame)) {
                std::cerr << "发送图像失败" << std::endl;
            }

            no_motion_count = 0;
        } else {
            no_motion_count++;
            if (no_motion_count >= NO_MOTION_THRESHOLD) {
                // 每隔一段时间输出一次状态
                if (no_motion_count % 100 == 0) {
                    std::cout << "监控中... (无运动)" << std::endl;
                }
            }
        }

        // 控制帧率
        usleep(1000000 / config.fps);
    }

    std::cout << "清理资源..." << std::endl;
    detector.release();
    sender.disconnect();

    std::cout << "系统已退出" << std::endl;
    return 0;
}
