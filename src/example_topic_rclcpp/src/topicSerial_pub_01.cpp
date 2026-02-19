#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include "serial/serial.h"


class topicSerial_pub_01 : public rclcpp::Node
{
    public:

    topicSerial_pub_01(std::string nodeName):Node(nodeName)
    {
        TopicPuber_ = this->create_publisher<std_msgs::msg::String>("pubtopicName",10);
        RCLCPP_INFO(this->get_logger(), "创建Puber,topicName: '%s'", TopicPuber_->get_topic_name());
        
        timer_ = this->create_wall_timer(std::chrono::milliseconds(500),std::bind(&topicSerial_pub_01::timer_callback,this));

        try
        {
            serial_port_.setPort("/dev/ttyACM0");
            serial_port_.setBaudrate(115200);
            serial::Timeout to = serial::Timeout::simpleTimeout(1000);
            serial_port_.setTimeout(to);
            serial_port_.open();
        }
        catch (serial::IOException &e)
        {
            RCLCPP_ERROR(this->get_logger(), "Unable to open port");
        }

        if (serial_port_.isOpen())
        {
            RCLCPP_INFO(this->get_logger(), "Serial Port initialized");
        }
        else
        {
            RCLCPP_ERROR(this->get_logger(), "Serial Port not initialized");
        }

    }

    private:

    serial::Serial serial_port_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr TopicPuber_;
    rclcpp::TimerBase::SharedPtr timer_;
    void timer_callback()
    {
        // std_msgs::msg::String message;
        // message.data="messageText";
        // TopicPuber_->publish(message);
        // RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
        if (serial_port_.available())
        {
            std::string data = serial_port_.readline(10, "\n");
            auto message = std_msgs::msg::String();
            message.data = data;
            RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
            TopicPuber_->publish(message);
        }
    }
};
int main(int argc, char **argv)
{
    //初始化
    rclcpp::init(argc,argv);
    //开辟节点空间
    auto node_share=std::make_shared<topicSerial_pub_01>("nodeName");
    //info
    RCLCPP_INFO(node_share->get_logger(),"启动Node: '%s'", node_share->get_name());
    //运行节点，并检测退出信号 Ctrl+C
    rclcpp::spin(node_share);
    //停止节点
    rclcpp::shutdown();

    return 0;
}