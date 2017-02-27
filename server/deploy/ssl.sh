#! /bin/sh

openssl genrsa -des3 -passout pass:x \
    -out server.pass.key 2048

openssl rsa -passin pass:x \
    -in server.pass.key \
    -out server.key

rm server.pass.key

openssl req -new \
    -key server.key \
    -out server.csr \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Global Security/OU=IT Department/CN=example.com"

openssl x509 -req -sha256 -days 365 \
    -in server.csr \
    -signkey server.key \
    -out server.crt

sudo cp server.key server.csr /etc/ssl/

rm server.key server.csr
