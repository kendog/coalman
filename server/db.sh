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