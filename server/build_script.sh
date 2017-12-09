#!/bin/sh

DATABASE_ROOT_PASS="changethispassword"
DATABASE_USER_PASS="changethispassword"

# Base
sudo yum -y clean all
sudo yum -y update

# Apache
sudo yum -y install httpd
sudo systemctl start httpd
sudo systemctl enable httpd

# Virtual Host Config
sudo mkdir /etc/httpd/sites-available
sudo mkdir /etc/httpd/sites-enabled

sudo mkdir -p /var/www/coalman.io
sudo mkdir -p /var/www/demo.coalman.io
sudo chown -R apache:apache /var/www/coalman.io
sudo chown -R apache:apache /var/www/demo.coalman.io
sudo chmod -R 755 /var/www/

# DB
# install mysql
sudo yum -y install mariadb-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
#sudo mysql_secure_installation
mysqladmin -u root password "$DATABASE_PASS"
mysql -u root -p"$DATABASE_PASS" -e "UPDATE mysql.user SET Password=PASSWORD('$DATABASE_ROOT_PASS') WHERE User='root'"
mysql -u root -p"$DATABASE_PASS" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
mysql -u root -p"$DATABASE_PASS" -e "DELETE FROM mysql.user WHERE User=''"
mysql -u root -p"$DATABASE_PASS" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%'"
mysql -u root -p"$DATABASE_PASS" -e "FLUSH PRIVILEGES"
# create user
mysql -u root -p"$DATABASE_PASS" -e "CREATE USER 'coalman'@'localhost' IDENTIFIED BY '$DATABASE_USER_PASS'"
mysql -u root -p"$DATABASE_PASS" -e "CREATE USER 'coalman'@'%' IDENTIFIED BY '$DATABASE_USER_PASS'"
mysql -u root -p"$DATABASE_PASS" -e "GRANT ALL ON *.* TO 'coalman'@'localhost'"
mysql -u root -p"$DATABASE_PASS" -e "GRANT ALL ON *.* TO 'coalman'@'%'"
# create db
mysql -u root -p"$DATABASE_PASS" -e "DROP DATABASE IF EXISTS coalman"
mysql -u root -p"$DATABASE_PASS" -e "CREATE DATABASE coalman"
# allow httpd
sudo setsebool -P httpd_can_network_connect_db on


# Requirements
sudo yum -y install git
sudo yum -y install mod_wsgi

#pull
sudo git clone https://github.com/kendog/coalman.git /var/www/coalman.io
sudo chown -R apache:apache /var/www/coalman.io/uploads/
sudo cp /var/www/coalman.io/server/etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf
sudo cp /var/www/coalman.io/server/etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/ssl.conf
sudo cp /var/www/coalman.io/server/etc/httpd/sites-available/coalman.io.conf /etc/httpd/sites-available/coalman.io.conf
sudo cp /var/www/coalman.io/server/etc/httpd/sites-available/demo.coalman.io.conf /etc/httpd/sites-available/demo.coalman.io.conf

#sudo cp /var/www/coalman.io/server/var/www/demo.coalman.io/index.html /var/www/demo.coalman.io/index.html

sudo ln -s /etc/httpd/sites-available/coalman.io.conf /etc/httpd/sites-enabled/coalman.io.conf
sudo ln -s /etc/httpd/sites-available/demo.coalman.io.conf /etc/httpd/sites-enabled/demo.coalman.io.conf

sudo mv /var/www/coalman.io/config-sample.py /var/www/coalman.io/config.py
sudo vi /var/www/coalman.io/config.py # and make edits



# Python Flask Requirements
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
sudo python get-pip.py
sudo pip install -r /var/www/coalman.io/requirements.txt




sudo systemctl restart httpd
#sudo systemctl restart mariadb
#sudo cat /var/log/httpd/error_log

#selinux...  need a permanent solution
#setenforce 0
# Set to permissive
sudo vi /etc/sysconfig/selinux

sudo service httpd restart

