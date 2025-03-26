apt update
if [ $? -ne 0 ]; then
	exit 1
fi
apt install -y apt-transport-https ca-certificates curl software-properties-common
if [ $? -ne 0 ]; then
	exit 2
fi
curl -fsSL https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
if [ $? -ne 0 ]; then
	exit 3
fi
add-apt-repository -y "deb https://download.sublimetext.com/ apt/stable/"
if [ $? -ne 0 ]; then
	exit 4
fi
apt update
if [ $? -ne 0 ]; then
	exit 5
fi
apt install -y sublime-text
if [ $? -ne 0 ]; then
	exit 6
fi
