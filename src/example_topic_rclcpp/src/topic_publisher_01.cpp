#include "rclcpp/rclcpp.hpp"

#include "std_msgs/msg/string.hpp"
class topic_publisher_01 : public rclcpp::Node
{
    public:

    topic_publisher_01(std::string nodeName):Node(nodeName)
    {
        TopicPuber_ = this->create_publisher<std_msgs::msg::String>("topic_t1",10);
        RCLCPP_INFO(this->get_logger(), "创建Puber,topicName: '%s'", TopicPuber_->get_topic_name());
        
        timer_ = this->create_wall_timer(std::chrono::milliseconds(500),std::bind(&topic_publisher_01::timer_callback,this));

    }

    private:

    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr TopicPuber_;
    rclcpp::TimerBase::SharedPtr timer_;
    void timer_callback()
    {
        std_msgs::msg::String message;
        message.data="messageText";
        TopicPuber_->publish(message);
        RCLCPP_INFO(this->get_logger(), "Publishing: '[%s]'", message.data.c_str());
    }
};
int main(int argc, char **argv)
{
    //初始化
    rclcpp::init(argc,argv);
    //开辟节点空间
    auto node_share=std::make_shared<topic_publisher_01>("nodeName");
    //info
    RCLCPP_INFO(node_share->get_logger(),"启动Node: '%s'", node_share->get_name());
    //运行节点，并检测退出信号 Ctrl+C
    rclcpp::spin(node_share);
    //停止节点
    rclcpp::shutdown();

    return 0;
}
