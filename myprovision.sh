#!/usr/bin/env bash

echo "Start!"

sudo apt update
sudo apt -y upgrade

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 2

sudo apt install tree


if ! [ -e /vagrant/mysql-apt-config_0.8.18-1_all.deb ]; then
	wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.18-1_all.deb
fi
sudo dpkg -i mysql-apt-config_0.8.18-1_all.deb
sudo DEBIAN_FRONTEND=noninteractivate apt install -y mysql-server
sudo apt install -y libmysqlclient-dev

# setup pip
if [ ! -f "/usr/bin/pip" ]; then
  sudo apt install -y python3-pip
  sudo apt install -y python-setuptools
  sudo ln -s /usr/bin/pip3 /usr/bin/pip
else
  echo "pip3 installed"
fi

# python dependencies
sudo apt install -y python3-testresources
pip install --upgrade setuptools
pip install --ignore-installed wrapt
pip install -U pip
pip install -r /vagrant/requirements.txt

# django admin
sudo apt install -y python3-django

# setup mysql and database
sudo mysql -u root << EOF
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'pw';
	flush privileges;
	show databases;
	CREATE DATABASE IF NOT EXISTS tweeter;
EOF


echo 'All Done!'