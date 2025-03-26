apt update
if [ $? -ne 0 ]; then
	exit 1
fi
apt install -y mc git tio minicom fritzing fritzing-data fritzing-parts gcc g++ make libncurses5-dev gawk pkg-config python3-matplotlib python3-distutils-extra
if [ $? -ne 0 ]; then
	exit 2
fi
