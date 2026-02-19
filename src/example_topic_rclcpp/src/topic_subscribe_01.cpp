// #include "rclcpp/rclcpp.hpp"

// #include "std_msgs/msg/string.hpp"
// class topic_subscribe_01 : public rclcpp::Node
// {
//     public:

//     topic_subscribe_01(std::string nodeName):Node(nodeName)
//     {
//         TopicSuber_ = this->create_subscription<std_msgs::msg::String>("topic_t1", 10, std::bind(&topic_subscribe_01::suber_callback, this, std::placeholders::_1));
//         RCLCPP_INFO(this->get_logger(), "创建Suber,topicName: '%s'", TopicSuber_->get_topic_name());
//     }

//     private:

//     rclcpp::Subscription<std_msgs::msg::String>::SharedPtr TopicSuber_;

//     void suber_callback(const std_msgs::msg::String::SharedPtr msg)
//     {
//         if(msg->data == "messageText")
//         {
//             //exe
//         }
//         RCLCPP_INFO(this->get_logger(), "收到data:[%s]", msg->data.c_str());
//     }
// };
// int main(int argc, char **argv)
// {
//     //初始化
//     rclcpp::init(argc,argv);
//     //开辟节点空间
//     auto node_share=std::make_shared<topic_subscribe_01>("node_sub01");
//     //info
//     RCLCPP_INFO(node_share->get_logger(),"启动Node: '%s'", node_share->get_name());
//     //运行节点，并检测退出信号 Ctrl+C
//     rclcpp::spin(node_share);
//     //停止节点
//     rclcpp::shutdown();

//     return 0;
// }
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
class topic_subscribe_01: public rclcpp::Node
{
    public:

    topic_subscribe_01(std::string nodeName):Node(nodeName)
    {
        TopicSuber_ = this->create_subscription<std_msgs::msg::String>("topic_t1", 10, std::bind(&topic_subscribe_01::suber_callback, this, std::placeholders::_1));
        RCLCPP_INFO(this->get_logger(), "创建Suber,topicName: '%s'", TopicSuber_->get_topic_name());
    }

    private:

    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr TopicSuber_;

    void suber_callback(const std_msgs::msg::String::SharedPtr msg)
    {
        if(msg->data == "messageText")
        {
            //exe
        }
        RCLCPP_INFO(this->get_logger(), "收到data:[%s]", msg->data.c_str());
    }
};
int main(int argc, char **argv)
{
    //初始化
    rclcpp::init(argc,argv);
    //开辟节点空间
    auto node_share=std::make_shared<topic_subscribe_01>("nodesub");
    //info
    RCLCPP_INFO(node_share->get_logger(),"启动Node: '%s'", node_share->get_name());
    //运行节点，并检测退出信号 Ctrl+C
    rclcpp::spin(node_share);
    //停止节点
    rclcpp::shutdown();

    return 0;
}