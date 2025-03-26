su - "student-en" <<!
student
wget --directory-prefix=/tmp/ http://$1:8000/home_user.tar
if [ $? -ne 0 ]; then
	exit 1
fi
cd && find /home/student-en/ -mindepth 1 -maxdepth 1 -name '*' -exec rm -rf '{}' \; && tar -xf /tmp/home_user.tar
if [ $? -ne 0 ]; then
	exit 2
fi
rm /tmp/home_user.tar
wget --directory-prefix=/tmp/ http://$1:8000/pam_environment
if [ $? -ne 0 ]; then
	exit 3
fi
mv /tmp/pam_environment .pam_environment
if [ $? -ne 0 ]; then
	exit 4
fi
# add dobot to bashrc
echo "source /opt/magician_ros2_control_system/install/setup.bash" >> /home/student-en/.bashrc
echo "export ROS_LOCALHOST_ONLY=1" >> /home/student-en/.bashrc
echo "export MAGICIAN_TOOL=suction_cup" >> /home/student-en/.bashrc
echo "source /opt/ros2_realsense_camera/install/setup.bash" >> /home/student-en/.bashrc
!
