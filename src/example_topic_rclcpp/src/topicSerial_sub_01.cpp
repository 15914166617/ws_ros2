#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

#include "serial/serial.h"



class topicSerial_sub_01: public rclcpp::Node
{
    public:

    topicSerial_sub_01(std::string nodeName):Node(nodeName)
    {
        TopicSuber_ = this->create_subscription<std_msgs::msg::String>("SubtopicName", 10, std::bind(&topicSerial_sub_01::suber_callback, this, std::placeholders::_1));
        RCLCPP_INFO(this->get_logger(), "创建Suber,topicName: '%s'", TopicSuber_->get_topic_name());

        // serial_port_.Open("/dev/ttyUSB0");
        // serial_port_.Open("/dev/ttyACM0");
        // serial_port_.SetBaudRate(BaudRate::BAUD_9600);
        // serial_port_.SetCharacterSize(CharacterSize::CHAR_SIZE_8);
        // serial_port_.SetStopBits(StopBits::STOP_BITS_1);
        // serial_port_.SetParity(Parity::PARITY_NONE);

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


    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr TopicSuber_;
    // mutable  SerialStream serial_port_;
    // serial::Serial serial_port_;

    void suber_callback(const std_msgs::msg::String::SharedPtr msg)
    {
        RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());
        // serial_port_ << msg->data;
        //  unsigned char buffer[1] = {'a'};  
        //  unsigned char buffer[1] = {'c'};  
        if (msg->data.back() != '\n') {
            msg->data += '\n';
        }
         serial_port_.write(msg->data.c_str()); 
    }
    
};
int main(int argc, char **argv)
{
    //初始化
    rclcpp::init(argc,argv);
    //开辟节点空间
    auto node_share=std::make_shared<topicSerial_sub_01>("nodeSerial_sub");
    //info
    RCLCPP_INFO(node_share->get_logger(),"启动Node: '%s'", node_share->get_name());
    //运行节点，并检测退出信号 Ctrl+C
    rclcpp::spin(node_share);
    //停止节点
    rclcpp::shutdown();

    return 0;
}