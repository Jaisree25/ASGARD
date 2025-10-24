#!/usr/bin/env python3
import rclpy
from sensor_msgs.msg import JointState
import sys
import tty
import termios

# Initialize ROS2
rclpy.init()

# Create a node
node = rclpy.create_node('joint_teleop')

# Create publisher
publisher = node.create_publisher(JointState, 'joint_command', 10)

# Joint names for the robot arm
joint_names = ["Rotation", "Pitch", "Elbow", "Wrist_Pitch", "Wrist_Roll", "Jaw"]

# Current positions of all joints (start at zero)
positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# Which joint we're controlling (0-5)
current_joint = 0

# How much to move per keypress
step = 0.05

print("=== Joint Teleop ===")
print("Keys: 1-6 (select joint), +/- (move up/down), R (reset position), Q (quit)")

# Save terminal settings so we can restore them later
settings = termios.tcgetattr(sys.stdin)

# Set terminal to raw mode (reads one key at a time without Enter)
tty.setraw(sys.stdin.fileno())

try:
    while rclpy.ok():
        # Read one key from keyboard
        key = sys.stdin.read(1)
        
        # Select joint if key is 1-6
        if key in '123456':
            current_joint = int(key) - 1
        
        # Increase position if key is +
        if key == '+':
            positions[current_joint] = positions[current_joint] + step
            if positions[current_joint] > 3.14:
                positions[current_joint] = 3.14
        
        # Decrease position if key is -
        if key == '-':
            positions[current_joint] = positions[current_joint] - step
            if positions[current_joint] < -3.14:
                positions[current_joint] = -3.14
        
        # Reset all joints if key is R
        if key.lower() == 'r':
            positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        # Quit if key is Q
        if key.lower() == 'q':
            break
        
        # Create message
        msg = JointState()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.name = joint_names
        msg.position = positions
        
        # Publish message
        publisher.publish(msg)
        
        # Let ROS2 process any incoming messages
        rclpy.spin_once(node, timeout_sec=0)

except KeyboardInterrupt:
    pass

finally:
    # Restore terminal to normal mode
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    # Cleanup
    node.destroy_node()
    rclpy.shutdown()
