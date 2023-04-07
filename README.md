# ChatGPT plugin sample.
OpenAI ChatGPT plugin sample  
* [Introduction](https://platform.openai.com/docs/plugins/introduction)  
* [Getting started](https://platform.openai.com/docs/plugins/getting-started/plugin-manifest)  
* [Examples](https://platform.openai.com/docs/plugins/examples)  
## Overview
This is a basic web parser plugin that retrieves text and links from a webpage based on the URL provided in the ChatGPT prompt. This enables ChatGPT to browse the web and gather current information.
## Requirements
* Access to the limited alpha of Chat plugins. Join the (ChatGPT plugins waitlist here!)[https://openai.com/waitlist/plugins]  
* Linux machine with external static IP address  
* Domain name  
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
### 3. Certificate installation
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
  
### 4. Check the docker-compose.yml file
Update the domain name in docker-compose.yml
### 5. Run the container
```
docker-compose up --build -d
```
### 6. Install your plugin in ChatGPT UI
* Go to [https://chat.openai.com/chat](https://chat.openai.com/chat)
* Select model: Plugins ALPHA
* Select Plugin: Plugin store
* Click on "Develop your own plugin"
* Click on "My manifest is ready"
* Enter your domain name, for example: https://your-domain.com and click on "Find manifest file"
* Click on "Next"
* Click on "Install for me"
* Click on "Continue"
* Click on "Install plugin"
### 7. Use your plugin
With the chosen plugin, write the prompt, containing request to your plugin. For example:
```
Please, describe, what is site langtea.club about?
```
### Additional resources:
* Useful video: [ChatGPT Plugins: Build Your Own in Python!](https://youtu.be/hpePPqKxNq8)
* (Official chatgpt-retrieval-plugin sample repo)[https://github.com/openai/chatgpt-retrieval-plugin]
* (Officiall examples)[https://platform.openai.com/docs/plugins/examples]
