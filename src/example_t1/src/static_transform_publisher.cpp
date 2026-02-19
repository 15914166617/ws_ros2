#include <rclcpp/rclcpp.hpp>
#include <tf2_ros/static_transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>

//1
//ros2  launch example_t1 text1.launch.py   会启动rviz与slam
//ros2 bag play rosbag2_2024_08_24-09_30_17_0.db3 -l  会启动播放录制好的反馈给ros2的建图数据
//这可以测试建图包car是否正常

//节点模拟发布了静态tf,本来是准备把其他数据通过串口发送过来，进行建图测试，现在准备在下位机器使用microros所以暂时不用了
//这里会发布tf static,细节部分可能还需要修改
class StaticTransformPublisher : public rclcpp::Node
{
public:
    StaticTransformPublisher() : Node("static_transform_publisher")
    {
        static_broadcaster_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(this);

        // 发布第一个变换：base_link -> imu_Link
        geometry_msgs::msg::TransformStamped transformStamped;
        transformStamped.header.stamp = rclcpp::Time(0);
        transformStamped.header.frame_id = "base_link";
        transformStamped.child_frame_id = "imu_Link";
        transformStamped.transform.translation.x = 0.0;
        transformStamped.transform.translation.y = 0.0;
        transformStamped.transform.translation.z = 0.0529999999999999;
        transformStamped.transform.rotation.x = 0.0;
        transformStamped.transform.rotation.y = 0.0;
        transformStamped.transform.rotation.z = 0.0;
        transformStamped.transform.rotation.w = 1.0;
        static_broadcaster_->sendTransform(transformStamped);

        // 发布第二个变换：imu_Link -> scan_Link
        transformStamped.header.frame_id = "imu_Link";
        transformStamped.child_frame_id = "scan_Link";
        transformStamped.transform.translation.z = 0.04;
        static_broadcaster_->sendTransform(transformStamped);

        // 发布第三个变换：base_link -> wheelF_Link
        transformStamped.header.frame_id = "base_link";
        transformStamped.child_frame_id = "wheelF_Link";
        transformStamped.transform.translation.x = 0.057;
        transformStamped.transform.translation.z = 0.00649999999999992;
        static_broadcaster_->sendTransform(transformStamped);

        RCLCPP_INFO(this->get_logger(), "Published static transforms to /tf_static.");
    }

private:
    std::shared_ptr<tf2_ros::StaticTransformBroadcaster> static_broadcaster_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<StaticTransformPublisher>());
    rclcpp::shutdown();
    return 0;
}
