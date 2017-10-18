# Private key

-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAuppOg8RnxJ5PKnO5hrbdG2wUOxS5F7jICUJSuW3McRQA4XeJ
PtDHgmY7u2Gu8fwnguW9VXQzoNeG9R7on9zlyfkcS6iVwPVlAo95+jloCv8iKBiq
Df7mcbLZY2p5dDNCOZp0WqDwrROAV6T9kTIEzuN4sdhz3EktwlZem3Ku7IhIelLY
WhBuxTnV5/bauvtfQWUGhpbKubE3uvXrZz20V6uIQcmkH77sXYo00D0acGXG68Bu
4YqvRVMMAq7tO+FKPLzYwipZTl50gUn2ojd+kigIJNrGBecVvWaNib9T3HrGwTxM
JBaiR0rZAkTRWzDNlVk/aRrCO7CjzAJ7WhiZ6wIDAQABAoIBAQCdCs43IO0/0QfJ
L3mdAXrV4ECqdEdNyoo3GKUsP1bGd9JB7msH/YdanBV7HruwFcle5WBRcakdnSWM
V4XpPGv7bfY9SlU1/pAS9pLuXq/MSWoCmrdLbhGc8Kr5extaCuWaOv3fZAEJeBcU
K9vm/VSElXX3HrZrVv72xd97Lao/jwRxxCD/BdNInFGub1MdCtinWSBJW0fNl3aQ
RrXbMFO6LeU/D2nV1DV3h04t4raewmBYcL5ekGP74Y57cCamDK9Jaq/bfGWcUw0a
EFURfUzpTKtbLQotkW/wGi3arZ2RMJobpzMfTBonMjQuNiRZx2J5y5xd3AGIn5o2
21SW+38BAoGBAPPRVUdyegHp8pAOPUeeA62l5NPnprl1MKJtX85oMuX/ZyKulU6o
EScYJsmD+uqwKa6bG6N0Ivb854x8Ax3ge8mx71LwKy0pX/FKHMbHJ5rySkKVf5RG
oe8nQkxY78sYp7wwiUHV7m568oAZvalvgMQdAleS/Zqxfny5jNkCqKiBAoGBAMPt
I3I1vc1PDpSlJ9gTB8XyByn4uDmpsIrxzNXk5V99hqWmkMh1aw60c0yHWqr7+G00
IEutzBy5EgXfj8B+fmNZ/3kQk5LUNNf0SB246vD05S5cP0nHIBFV2iYzgoRr4usY
TGBxpjdNF9HlPFQJw/wdoYQzVNKGGfw6sG9OpCxrAoGAN9WYUeRFTGrmwVaBcgUd
koaLAHvsEkxj9s5VQk9aWJFEbQzN5FVYmDtPppYyv8vXv8SFb8kIuMbxv5omnJDr
yCSXScb2HEF9VyRBssOorjMODnFt5ebG7p1u8UzsnPXoc5Ap3om/ME23et5qMIL4
WfDKuINQ0DwVWzqipo+VUAECgYAKQ1zM+cW0gISqArDAn9aTZuc7Kp0z4BCwZpQt
TC07wE6SVNRWu9fc0FUN2DVGqaZMyiM686KyintINXrJQZcLS0aXp+ejFFykR1aT
wAEGmD19HTXvfm/OmKmxwJcAqsobOI2fq7RiRzaNNy3e1RggF8lDLJEv6fhofwaI
/hyZewKBgQCBx2SzQ1y6ucZ6RedubkWj+5vv8MKu78DY7b9vkJnN6Zchvq4vEyUt
VV6QY2EwBj6tLSF6uXPcHc4RZwAz5R+RqvByBMIHbnKn/t2LndZBqhyssBXqNxg6
Vbn4h5L6ZAQ3OA81QNI+NSkqWvtHstA6zoNS4Sy0UxgQZ+g0PZZgUA==
-----END RSA PRIVATE KEY-----



# Create an Instance on AWS Lightsail
The public IP address of the instance is displayed along with its name. In the above picture it's 54.93.199.41. The DNS name of this instance is ec2-54-93-199-41.compute-1.amazonaws.com.

Under these addresses you can visit the webapp:

* http://54.93.243.251

* ec2-54-93-199-41.compute-1.amazonaws.com

# Login to the server the first timezone

* Download the default rsa key

* Move it in your working folder

* Login ssh -i LightsailDefaultPrivateKey-eu-central-1.pem ubuntu@54.93.243.251

* Update server

`sudo apt-get update`

`sudo apt-get upgrade -y`

`sudo apt-get install unattended-upgrades`

`sudo dpkg-reconfigure -plow unattended-upgrades`

# Adding a new user correctly
Create a local key pair locally:

`ssh-keygen`

On server:

`sudo adduser grader`

`sudo vim /etc/sudoers.d/grader`

Write:
`grader ALL=(ALL) NOPASSWD:ALL`

Login to user

`sudo su - grader`

`mkdir .ssh`

`chmod 700`

`vim .ssh/authorized_keys`

copy public key & save it
`chmod 644 .ssh/authorized_keys`

`vim /etc/ssh/sshd_config`
Change Port 22 to Port 2200

Allow port 2200 on firewall via amazon lightsail website.

Ubuntu Login
`ssh -i LightsailDefaultPrivateKey-eu-central-1.pem -p 2200 ubuntu@54.93.243.251`

Grader Login
`ssh -i grader_key_udactiy_last_project.rsa -p 2200 grader@54.93.243.251`

# Setup server

* sudo ufw default deny incoming

* sudo ufw default allow outgoing

* sudo ufw status

* sudo ufw allow ssh

* sudo ufw allow 2200/tcp

* sudo ufw allow 80

* sudo ufw allow 123

* sudo ufw enable

* sudo ufw status verbose

# Installs

* sudo apt-get install git

(should already be installed)

Python installations:

* sudo apt install python-minimal

* sudo apt-get -qqy install python-pip

* sudo apt install redis-server

* sudo pip install flask

* sudo pip install redis

* sudo pip install sqlalchemy

* sudo pip install httplib2

* sudo pip install passlib

* sudo pip install oauth2client

* sudo pip install requests

Apache2:

* sudo apt-get install apache2

* sudo apt-get install libapache2-mod-wsgi

* sudo apt-get install postgresql

# Change timezone

`sudo timedatectl set-timezone UTC`

# Postgres configuration

change user to postgres

`sudo -i -u postgres`

Create a new data base called catalog

`postgres@server:~$ createuser --interactive -P`

`Enter name of role to add: catalog`

`Enter password for new role:`

`Enter it again:`

`Shall the new role be a superuser? (y/n) n`

`Shall the new role be allowed to create databases? (y/n) n`

`Shall the new role be allowed to create more new roles? (y/n) n`

Create catalog Database

`psql`

`CREATE DATABASE catalog;`

`\q`

Logout

`exit`

# Test your server the first time

* Visit http://54.93.243.251

* You should see a website with an Ubuntu Logo the title "Apache2 Ubuntu Default Page"

* You can also test with `curl http://localhost`

# Copying your repo

The default web root is */var/www*. Therefore we will copy our repo there. [Here a link for further reading](https://www.digitalocean.com/community/questions/what-is-the-correct-folder-to-put-my-website-files-var-www-or-var-www-html)

`sudo git clone https://github.com/Charistoph/item_catalog.git`

# Protect .git folder

`sudo chmod 700 /var/www/item_catalog/.git`

# Write your wsgi.py file

`import sys

sys.path.insert(0, '/var/www/catalog')

from catalog import app as application

application.secret_key = 'New secret key. Change it on server'

application.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://'
    'catalog:password@localhost/catalog')`


# Update Database connection string in database_setup to the following:

`postgresql://catalog:password@localhost/catalog`

# Change conf file

`sudo vim /etc/apache2/sites-available/catalog.conf`

Add

`<VirtualHost *:80>
    ServerName 54.93.243.251

    WSGIScriptAlias / /var/www/catalog/wsgi.py

    <Directory /var/www/catalog>
        Order allow,deny
        Allow from all
    </Directory>
</VirtualHost>`

# Error

mod_wsgi (pid=7830): Target WSGI script '/var/www/catalog/wsgi.py' cannot be loaded as Python module.

What can be done about this?

# Login

ssh -i grader_key_udactiy_last_project.rsa -p 2200 grader@54.93.243.251
