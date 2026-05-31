#!/bin/bash
set -e

echo "creating SSL certificates and keys"

# Go to the proper directory
cd /var/lib/postgresql/data

# Generate root certificate authority (CA)
openssl req -new -x509 -days 365 -nodes -out root.crt -keyout root.key -subj "/CN=root-ca"
chmod 600 root.key  # private key data that must be kept secret

# Generate private key
openssl genrsa -out server.key 2048
chmod 600 server.key  # private key data that must be kept secret

# Generate server certificate signing request
openssl req -new -key server.key -out server.csr -subj "/CN=anonymous"

# Sign the server certificate with root CA
openssl x509 -req -in server.csr -CAkey root.key -CA root.crt -out server.crt -CAcreateserial -days 999999 -subj "/C=ZZ"
chmod 644 server.crt
