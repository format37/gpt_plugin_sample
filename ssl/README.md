Put your SSL files there:  
cert.pem  
key.pem  
```
openssl genrsa -out key.pem 2048
openssl req -new -x509 -days 3650 -key key.pem -out cert.pem
```
When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply  
with the same value in you put in WEBHOOK_HOST  
for example:  
example.com