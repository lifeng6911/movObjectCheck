#ifndef MOTION_DETECTOR_H
#define MOTION_DETECTOR_H

#include <opencv2/opencv.hpp>
#include "config.h"

class MotionDetector {
public:
    MotionDetector(const Config& config);
    ~MotionDetector();

    bool initialize();
    bool detectMotion(cv::Mat& output_frame);
    void release();

private:
    bool isLightingChange(const cv::Mat& frame_delta, double motion_area);

    Config config_;
    cv::VideoCapture cap_;
    cv::Mat prev_frame_;
    bool motion_detected_;
    int frame_count_;
};

#endif // MOTION_DETECTOR_H
