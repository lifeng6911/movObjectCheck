#ifndef CONFIG_H
#define CONFIG_H

#include <string>

struct Config {
    // 摄像头配置
    int camera_index = 0;
    int frame_width = 640;
    int frame_height = 480;
    int fps = 15;

    // 运动检测参数
    int motion_threshold = 25;
    int min_area = 500;
    int lighting_threshold = 15;
    int background_update_interval = 30;

    // 网络配置
    std::string server_ip = "127.0.0.1";
    int server_port = 8888;
    int connection_timeout = 5000;

    // 传输配置
    int jpeg_quality = 80;
    int max_retry = 3;

    bool loadFromFile(const std::string& filename);
};

#endif // CONFIG_H
