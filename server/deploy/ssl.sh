#! /bin/sh

DEST="/etc/ssl/"
PASSKEY="${DEST}server.pass.key"
KEY="${DEST}server.key"
CRT="${DEST}server.crt"
CSR="${DEST}server.csr"

openssl genrsa -des3 -passout pass:x -out $PASSKEY 2048

openssl rsa -passin pass:x -in $PASSKEY -out $KEY

openssl req -new -key $KEY -out $CSR \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Global Security/OU=IT Department/CN=example.com"

openssl x509 -req -sha256 -days 365 -in $CSR -signkey $KEY -out $CRT

rm $PASSKEY
