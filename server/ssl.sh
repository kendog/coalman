sudo yum -y install mod_ssl
sudo cp /var/www/coalman.io/server/etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/ssl.conf

# Copy Certs to locations
#SSLCertificateFile /etc/pki/tls/certs/localhost.crt
sudo vi /etc/pki/tls/certs/coalman_io.crt

#SSLCertificateKeyFile /etc/pki/tls/private/localhost.key
sudo vi /etc/pki/tls/private/coalman_io.key

#SSLCertificateChainFile /etc/pki/tls/certs/server-chain.crt
sudo vi /etc/pki/tls/certs/server-chain.crt


#grep /etc/httpd/conf.d/ssl.conf.off -vEe ^# -vEe ^[[:space:]]*# -vEe ^[[:space:]]*$
