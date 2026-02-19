#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include <vector>
#include <cmath>

class LDSShadowNode : public rclcpp::Node {
public:
    LDSShadowNode() : Node("lds_shadow_node") {
        RCLCPP_INFO(this->get_logger(), "LDS Shadow Detection Node Started");

        subscription_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/scan", 20,
            std::bind(&LDSShadowNode::scan_callback, this, std::placeholders::_1));
    }

private:
    void scan_callback(const sensor_msgs::msg::LaserScan::SharedPtr msg) {
        size_t invalid_count = 0;
        size_t dropped_count = 0;
        size_t shadow_count = 0;

        // 连续点差异阈值（可调）
        const float jump_threshold = 0.2; // 米

        // 检查点数据
        for (size_t i = 0; i < msg->ranges.size(); ++i) {
            float r = msg->ranges[i];

            // 统计无效点
            if (!std::isfinite(r) || r <= 0.0) {
                invalid_count++;
            }

            // 检测掉点（这里假设 LDS size 不稳定可能是掉点）
            if (msg->ranges.size() != expected_size) {
                dropped_count++;
            }

            // 连续点跳变过大 → 可能重影
            if (i > 0) {
                float diff = std::fabs(r - msg->ranges[i - 1]);
                if (diff > jump_threshold) {
                    shadow_count++;
                }
            }
        }

        // 更新期望大小
        expected_size = msg->ranges.size();

        // 输出日志
        RCLCPP_INFO(this->get_logger(),
                    "Scan points: %zu | Invalid: %zu | Shadow jumps: %zu | Dropped points?: %zu",
                    msg->ranges.size(), invalid_count, shadow_count, dropped_count);
    }

    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscription_;
    size_t expected_size = 0;
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<LDSShadowNode>());
    rclcpp::shutdown();
    return 0;
}

// colcon build --packages-select lds_health