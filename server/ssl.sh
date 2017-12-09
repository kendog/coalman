sudo yum -y install mod_ssl

sudo vi /etc/httpd/conf.d/ssl.conf

#uncoment = SSLCertificateChainFile


SSLCertificateFile /etc/pki/tls/certs/localhost.crt

SSLCertificateKeyFile /etc/pki/tls/private/localhost.key

#SSLCertificateChainFile /etc/pki/tls/certs/server-chain.crt

grep /etc/httpd/conf.d/ssl.conf.off -vEe ^# -vEe ^[[:space:]]*# -vEe ^[[:space:]]*$



sudo cp /var/www/coalman.io/server/etc/httpd/conf/ssl.conf /etc/httpd/conf/ssl.conf
