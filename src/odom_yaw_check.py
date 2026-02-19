#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math

class OdomYawChecker(Node):
    def __init__(self):
        super().__init__('odom_yaw_checker')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.prev_yaw = None
        self.total_yaw = 0.0
        self.get_logger().info("Odom yaw checker started. Rotating small car...")

    def odom_callback(self, msg):
        q = msg.pose.pose.orientation
        yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))  # rad
        if self.prev_yaw is not None:
            delta = yaw - self.prev_yaw
            # 修正跨越 -pi 到 pi
            if delta > math.pi:
                delta -= 2*math.pi
            elif delta < -math.pi:
                delta += 2*math.pi
            self.total_yaw += delta
        self.prev_yaw = yaw
        print(f"Current yaw: {yaw:.4f} rad, Total accumulated yaw: {self.total_yaw:.4f} rad")

def main(args=None):
    rclpy.init(args=args)
    node = OdomYawChecker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(f"Final total yaw: {node.total_yaw:.4f} rad ({math.degrees(node.total_yaw):.2f} deg)")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
