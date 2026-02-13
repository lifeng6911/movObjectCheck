#include "motion_detector.h"
#include <opencv2/opencv.hpp>
#include <iostream>
#include <cmath>

MotionDetector::MotionDetector(const Config& config)
    : config_(config),
      motion_detected_(false),
      frame_count_(0) {
}

MotionDetector::~MotionDetector() {
}

bool MotionDetector::initialize() {
    cap_.open(config_.camera_index);
    if (!cap_.isOpened()) {
        std::cerr << "无法打开摄像头" << std::endl;
        return false;
    }

    cap_.set(cv::CAP_PROP_FRAME_WIDTH, config_.frame_width);
    cap_.set(cv::CAP_PROP_FRAME_HEIGHT, config_.frame_height);
    cap_.set(cv::CAP_PROP_FPS, config_.fps);

    // 预热摄像头，读取几帧以稳定曝光
    for (int i = 0; i < 10; i++) {
        cv::Mat temp;
        cap_ >> temp;
    }

    std::cout << "摄像头初始化成功" << std::endl;
    return true;
}

bool MotionDetector::detectMotion(cv::Mat& output_frame) {
    cv::Mat frame, gray, blur_frame;

    cap_ >> frame;
    if (frame.empty()) {
        std::cerr << "无法读取帧" << std::endl;
        return false;
    }

    frame_count_++;

    // 转换为灰度图
    cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

    // 高斯模糊，减少噪声
    cv::GaussianBlur(gray, blur_frame, cv::Size(21, 21), 0);

    // 初始化背景帧
    if (prev_frame_.empty()) {
        prev_frame_ = blur_frame.clone();
        output_frame = frame.clone();
        return false;
    }

    // 计算帧差
    cv::Mat frame_delta, thresh;
    cv::absdiff(prev_frame_, blur_frame, frame_delta);
    cv::threshold(frame_delta, thresh, config_.motion_threshold, 255, cv::THRESH_BINARY);

    // 膨胀操作，填充空洞
    cv::dilate(thresh, thresh, cv::Mat(), cv::Point(-1, -1), 2);

    // 查找轮廓
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(thresh, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    bool motion_found = false;
    double total_area = 0;

    // 分析轮廓
    for (const auto& contour : contours) {
        double area = cv::contourArea(contour);
        if (area < config_.min_area) {
            continue;
        }

        total_area += area;

        // 绘制检测框
        cv::Rect bounding_rect = cv::boundingRect(contour);
        cv::rectangle(frame, bounding_rect, cv::Scalar(0, 255, 0), 2);
        motion_found = true;
    }

    // 光照变化过滤
    if (motion_found && !isLightingChange(frame_delta, total_area)) {
        motion_detected_ = true;
        output_frame = frame.clone();

        // 更新背景帧（缓慢适应）
        if (frame_count_ % config_.background_update_interval == 0) {
            cv::addWeighted(prev_frame_, 0.95, blur_frame, 0.05, 0, prev_frame_);
        }

        return true;
    } else {
        // 更新背景帧
        if (frame_count_ % config_.background_update_interval == 0) {
            prev_frame_ = blur_frame.clone();
        }

        motion_detected_ = false;
        output_frame = frame.clone();
        return false;
    }
}

bool MotionDetector::isLightingChange(const cv::Mat& frame_delta, double motion_area) {
    // 计算整体亮度变化
    cv::Scalar mean_val = cv::mean(frame_delta);
    double mean_change = mean_val[0];

    // 如果整体亮度变化较大，且运动区域占比较大，可能是光照变化
    double frame_area = frame_delta.rows * frame_delta.cols;
    double motion_ratio = motion_area / frame_area;

    if (mean_change > config_.lighting_threshold && motion_ratio > 0.3) {
        std::cout << "检测到光照变化，忽略此次运动" << std::endl;
        return true;
    }

    return false;
}

void MotionDetector::release() {
    if (cap_.isOpened()) {
        cap_.release();
    }
}
