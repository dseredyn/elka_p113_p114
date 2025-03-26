#!/bin/bash

#su administrator

# ROS2
## Enable Ubuntu Universe repository
sudo apt install -y software-properties-common
if [ $? -ne 0 ]; then
	exit 1
fi
sudo add-apt-repository -y universe
if [ $? -ne 0 ]; then
	exit 2
fi
## Add ROS2 GPG key
sudo apt update
sudo apt install curl -y
if [ $? -ne 0 ]; then
	exit 3
fi
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
## Add repository to sources
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
## Update packages
sudo apt update
sudo apt upgrade -y
if [ $? -ne 0 ]; then
	exit 4
fi
## Install ROS2
sudo apt install -y ros-humble-desktop
if [ $? -ne 0 ]; then
	exit 5
fi
## Install ROS2 development tools
sudo apt install -y ros-dev-tools
if [ $? -ne 0 ]; then
	exit 6
fi

# Dobot
## Source ROS2
source /opt/ros/humble/setup.bash
## Install required packages
sudo apt install -y ros-humble-diagnostic-aggregator ros-humble-rqt-robot-monitor ros-humble-tf-transformations ros-humble-urdf-tutorial python3-pykdl python3-pip python3-rosdep2 python3-colcon-common-extensions
if [ $? -ne 0 ]; then
	exit 7
fi

## Init rosdep
sudo rosdep init
rosdep update
## Clone repository
cd
mkdir -p ~/magician_ros2_control_system/src
cd magician_ros2_control_system/
git clone https://github.com/GroupOfRobots/magician_ros2.git src/
if [ $? -ne 0 ]; then
	exit 8
fi

## Install dependencies
sudo pip3 install -r src/requirements.txt
if [ $? -ne 0 ]; then
	exit 9
fi

rosdep install -i --from-path src --rosdistro humble -y
if [ $? -ne 0 ]; then
	exit 10
fi

## Build
colcon build
if [ $? -ne 0 ]; then
	exit 11
fi

## Remove unnecesarry files
rm -rf build/ log/ src/
## Move packages to /opt
cd 
mv magician_ros2_control_system/ /opt
if [ $? -ne 0 ]; then
	exit 12
fi

## Refresh rqt cache
source /opt/magician_ros2_control_system/install/setup.bash
#rqt --force-discover
## Add users to dialout group
sudo adduser student-en dialout
sudo adduser student-pl dialout
## Add things to bash
echo "source /opt/magician_ros2_control_system/install/setup.bash" >> /home/student-pl/.bashrc
echo "source /opt/magician_ros2_control_system/install/setup.bash" >> /home/student-en/.bashrc
echo "export ROS_LOCALHOST_ONLY=1" >> /home/student-pl/.bashrc
echo "export ROS_LOCALHOST_ONLY=1" >> /home/student-en/.bashrc
echo "export MAGICIAN_TOOL=suction_cup" >> /home/student-pl/.bashrc
echo "export MAGICIAN_TOOL=suction_cup" >> /home/student-en/.bashrc

# Realsense
## Install apt libraries
sudo mkdir -p /etc/apt/keyrings
curl -sSf https://librealsense.intel.com/Debian/librealsense.pgp | sudo tee /etc/apt/keyrings/librealsense.pgp > /dev/null
sudo apt-get -y install apt-transport-https
if [ $? -ne 0 ]; then
	exit 13
fi

echo "deb [signed-by=/etc/apt/keyrings/librealsense.pgp] https://librealsense.intel.com/Debian/apt-repo `lsb_release -cs` main" | \
sudo tee /etc/apt/sources.list.d/librealsense.list
sudo apt-get update
sudo apt-get -y install librealsense2-dkms librealsense2-utils librealsense2-dev librealsense2-dbg
if [ $? -ne 0 ]; then
	exit 14
fi
## Install dependencies from pip
sudo pip3 install opencv-contrib-python==4.6.0.66
sudo apt-get install -y ros-humble-librealsense2 ros-humble-diagnostic-updater
if [ $? -ne 0 ]; then
	exit 15
fi

## Clone repository
mkdir -p ~/ros2_realsense_camera/src && cd ~/ros2_realsense_camera/src/
git clone https://github.com/IntelRealSense/realsense-ros.git -b ros2-development
if [ $? -ne 0 ]; then
	exit 16
fi

cd realsense-ros/
git branch specific-commit-branch 5c298f7
git switch specific-commit-branch
cd ..
## Install dependencies
cd .. && source /opt/ros/humble/setup.bash && rosdep update
rosdep install -i --from-path src --rosdistro humble -y
if [ $? -ne 0 ]; then
	exit 17
fi

## Build workspace
colcon build
if [ $? -ne 0 ]; then
	exit 18
fi

## Remove unnecesarry files
rm -rf build/ log/ src/
## Move packages to /opt
cd ..
sudo mv ros2_realsense_camera/ /opt/
if [ $? -ne 0 ]; then
	exit 19
fi

## Add things to bash
echo "source /opt/ros2_realsense_camera/install/setup.bash" >> /home/student-pl/.bashrc
echo "source /opt/ros2_realsense_camera/install/setup.bash" >> /home/student-en/.bashrc

exit 0
