apt update
if [ $? -ne 0 ]; then
	exit 1
fi
apt install -y gnupg2 software-properties-common apt-transport-https wget
if [ $? -ne 0 ]; then
	exit 2
fi
wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add -
if [ $? -ne 0 ]; then
	exit 3
fi
add-apt-repository -y "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main"
if [ $? -ne 0 ]; then
	exit 4
fi
apt update
if [ $? -ne 0 ]; then
	exit 5
fi
apt install -y code
if [ $? -ne 0 ]; then
	exit 6
fi
