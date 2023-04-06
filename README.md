# ChatGPT plugin sample
OpenAI ChatGPT plugin sample  
* [Introduction](https://platform.openai.com/docs/plugins/introduction)
* [Examples](https://platform.openai.com/docs/plugins/examples)
* [Manifest file](https://platform.openai.com/docs/plugins/getting-started/plugin-manifest)  
## Installation
### 1. Install Docker (if you don't have it)
```
wget -qO- https://get.docker.com/ | sh
sudo apt install python3-pip -y
sudo pip install docker-compose
```
### 2. Clone this repository
```
git clone https://github.com/format37/gpt_plugin_sample.git
cd gpt_plugin_sample
```
### 3. Certificate installation (recommended)
If you're using only Flask in a Docker container and not using Apache or Nginx, you can still obtain an SSL certificate from Let's Encrypt using Certbot with the standalone plugin. Follow these steps:  
  
1. Install Certbot. The commands below are for Debian/Ubuntu-based systems. For other systems, follow the instructions on the [Certbot website](https://certbot.eff.org/instructions).  
```
sudo apt update
sudo apt install certbot
```
2. Before running Certbot, make sure that port 80 (HTTP) is open and not being used by any other service. If your Flask application is running on this port, stop it temporarily.  
  
3. Run Certbot in standalone mode to obtain the SSL certificate. Replace example.com with your domain, and add any additional subdomains with the -d flag.
```
sudo certbot certonly --standalone -d example.com -d www.example.com
```
4. Follow the on-screen instructions. Certbot will automatically obtain the SSL certificate and store it in /etc/letsencrypt/live/example.com.  
  
5. Now you need to share the certificates as volumes with your Docker container. Modify your docker-compose.yml file to include these volumes:
```
services:
  file_sever:
    ...
    volumes:
      ...
      - /etc/letsencrypt/live/example.com/fullchain.pem:/ssl/cert.pem
      - /etc/letsencrypt/live/example.com/privkey.pem:/ssl/key.pem
    ...
```
6. Set up automatic renewal for your SSL certificate by adding a cron job. Open the crontab with:
```
sudo crontab -e
```
Add the following line to renew the certificate twice a day:
```
0 */12 * * * certbot renew --quiet
```
Save and exit the crontab.  
  
Remember to restart your Flask application and Docker container after obtaining the SSL certificate.  
  
Now you have successfully obtained an SSL certificate from Let's Encrypt using Certbot for your Flask application running in a Docker container.  
  
Note: Keep in mind that the standalone plugin requires stopping your Flask application and opening port 80 during the SSL certificate issuance and renewal process. This can cause brief downtime for your application. If possible, consider using a reverse proxy (like Nginx) in front of your Flask application to handle SSL termination, which will also provide additional benefits like better performance, security, and flexibility.  
  
#### Quick and dirty certificate installation (not recommended)
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

### 4. Check the docker-compose.yml file
Update the domain name
### 5. Run the docker-compose.yml file
```
docker-compose up --build -d
```
