#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <cstdint>

// 消息类型定义
enum MessageType : uint8_t {
    MSG_HEARTBEAT = 0x01,      // 心跳消息
    MSG_HEARTBEAT_ACK = 0x02,  // 心跳响应
    MSG_IMAGE_DATA = 0x03,     // 图像数据
    MSG_REGISTER = 0x04,       // 设备注册
    MSG_REGISTER_ACK = 0x05    // 注册响应
};

// 消息头结构（8字节）
struct MessageHeader {
    uint8_t type;              // 消息类型
    uint8_t reserved;          // 保留字段
    uint16_t device_id;        // 设备ID
    uint32_t data_length;      // 数据长度
} __attribute__((packed));

// 心跳消息（无额外数据）
struct HeartbeatMessage {
    MessageHeader header;
} __attribute__((packed));

// 注册消息
struct RegisterMessage {
    MessageHeader header;
    char device_name[32];      // 设备名称
    char location[64];         // 设备位置
} __attribute__((packed));

#endif // PROTOCOL_H
