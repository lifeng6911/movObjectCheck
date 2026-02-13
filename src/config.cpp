#include "config.h"
#include <fstream>
#include <sstream>
#include <iostream>

bool Config::loadFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "无法打开配置文件: " << filename << std::endl;
        return false;
    }

    std::string line;
    while (std::getline(file, line)) {
        // 跳过注释和空行
        if (line.empty() || line[0] == '#') {
            continue;
        }

        std::istringstream iss(line);
        std::string key, value;

        if (std::getline(iss, key, '=') && std::getline(iss, value)) {
            // 去除空格
            key.erase(0, key.find_first_not_of(" \t"));
            key.erase(key.find_last_not_of(" \t") + 1);
            value.erase(0, value.find_first_not_of(" \t"));
            value.erase(value.find_last_not_of(" \t") + 1);

            // 解析配置项
            if (key == "camera_index") camera_index = std::stoi(value);
            else if (key == "frame_width") frame_width = std::stoi(value);
            else if (key == "frame_height") frame_height = std::stoi(value);
            else if (key == "fps") fps = std::stoi(value);
            else if (key == "motion_threshold") motion_threshold = std::stoi(value);
            else if (key == "min_area") min_area = std::stoi(value);
            else if (key == "lighting_threshold") lighting_threshold = std::stoi(value);
            else if (key == "background_update_interval") background_update_interval = std::stoi(value);
            else if (key == "server_ip") server_ip = value;
            else if (key == "server_port") server_port = std::stoi(value);
            else if (key == "connection_timeout") connection_timeout = std::stoi(value);
            else if (key == "jpeg_quality") jpeg_quality = std::stoi(value);
            else if (key == "max_retry") max_retry = std::stoi(value);
        }
    }

    file.close();
    std::cout << "配置文件加载成功" << std::endl;
    return true;
}
