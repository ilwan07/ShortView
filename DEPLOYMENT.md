# Deployment guide

#### **Here are the instructions to deploy this webapp on your own server. If you encounter issues, you can refer to [this guide from DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu) which is well written, and from which part of the below guide is based. Note that this guide can be used to deploy any WSGI Django project.**

This project was written with Django, a Python framework to make webapps. As such, if you want to deploy the project in a specific way, you can refer to the [Django documentation](https://docs.djangoproject.com/en/5.2/) and the [Django deployment guide](https://docs.djangoproject.com/en/5.2/howto/deployment/).

In this guide, we will cover deployment on a Debian server (on a Raspberry Pi for example) with root privileges using Nginx and Gunicorn.

## Clone and prepare the project

Get in the command line of your Debian server (with SSH for example), then `cd` into  the directory in which you want to store the project.

Make sure to install everything we'll need with `sudo apt update` and then `sudo apt install python3-venv python3-dev nginx curl certbot python3-certbot-nginx`

Then clone the project with `git clone https://github.com/ilwan07/ShortView.git` then get into the new folder with `cd ShortView`.

Now, create a Python virtual environment with `python3 -m venv .venv` (Python 3 needs to be installed on the system, it's usually the case on most Linux distributions).

Then activate it with `source .venv/bin/activate`, we will now install the project requirements with `pip install -r requirements.txt` which will also allow us to use Django commands later on.

Now, we need to create a `.env` file to store sensitive information, but before we need to generate a secret key. You can generate one by executing `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` in the terminal.

Create the file with `nano .env` and fill it like this:

```bash
DJANGO_SECRET_KEY_SHORTVIEW = '[secret key here]'
EMAIL_HOST_PASSWORD_SHORTVIEW = '[email password here]'
```

Replace (without the square brackets) `[secret key here]` with the secret key you just generated, and replace `[email password here]` by the app specific password for the email you wish to use to send notifications (leave it blank if you don't want to use emails, it shouldn't cause issues). For a bit more security, you can change by hand some of the characters from the secret key, this will make it more "random" and therefore more secure.

Now, we need to edit the settings file. Still from the ShortView folder, open it with `nano website/settings.py`, then change the followings.

Disable debugging by changing to `DEBUG = False`, then put your own domain for the `WEB_DOMAIN` variable.

After that, go towards the end of the file, and in the email configuration section, change the variables to make your own email work (refer to the documentation of your email provider for specific configuration, don't change anything if you don't want to use emails, the authentiation will simply fail without raising blocking errors).

Finally, enable SSL security by uncommenting each line under the `SECURITY FEATURES` section.

Now, we need to prepare the database and the static files folder. While still in the ShortView directory with the venv activated, run `python manage.py makemigrations` then `python manage.py migrate` and finally `sudo mkdir /var/www/shortview` then `sudo .venv/bin/python manage.py collectstatic` (here we need to use sudo as the static files will get collected in a folder for which regular users don't have write permissions, we also need to indicate the full python path as the root user hasn't activated the venv).

Create a superuser with `python manage.py createsuperuser` and fill in the required information, you will have to be logged in as this user to access the administrator interface, we recommend naming this user `admin`.

We don't need to use the venv from now on, so you can disable it with the `deactivate` command.

## Create the socket and service

Now that the project is ready, we need to serve it so that  it can be accessed from the internet.

First, you need to get a domain or subdomain for the website. Then, in your domain provider interface, you need to create an A record and put the IPv4 address of your internet router in it, then in your router's interface you need to forward port 80 and port 443 to those same ports on your server (those are respectively the HTTP and HTTPS ports).

If you're using a firewall on your server (such as `ufw`), then you need to allow those two ports (with `ufw`, you can execute `sudo ufw allow 'Nginx Full'` directly).

We will now create a socket to listen for connections with `sudo nano /etc/systemd/system/shortview.socket` and fill it with the following content:

```ini
[Unit]
Description=shortview gunicorn socket

[Socket]
ListenStream=/run/shortview.sock

[Install]
WantedBy=sockets.target
```

Now, we need to create the service itself which will run the server when a connection will occur, create and open it with `sudo nano /etc/systemd/system/shortview.service` and put the following in the file:

```ini
[Unit]
Description=shortview gunicorn daemon
Requires=shortview.socket
After=network.target

[Service]
User=[your username]
Group=www-data
WorkingDirectory=/home/[your username]/ShortView
ExecStart=/home/[your username]/ShortView/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/shortview.sock \
          website.wsgi:application

[Install]
WantedBy=multi-user.target
```

By replacing (without the square brackets) `[your username]` by the username of the user which will run the webapp on your server, and eventually replace the `WorkingDirectory` and `ExecStart` paths if you did not clone the project in your home directory.

Now, enable and start the socket with `sudo systemctl enable --now shortview.socket`.

If you make any change to the config afterward, run `sudo systemctl daemon-reload` then `sudo systemctl restart shortview` for the changes to take effect.

## Deploy with Nginx

Now, create the Nginx config for this project with `sudo nano /etc/nginx/sites-available/shortview` and put this in the file:

```nginx
server {
    listen 80;
    server_name [your domain];

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/shortview/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/shortview.sock;
    }
}
```

By replacing (without the square brackets) `[your domain]` by the domain or subdomain you are using for the webapp.

And now enable it with `sudo ln -s /etc/nginx/sites-available/shortview /etc/nginx/sites-enabled/` then test its syntax with `sudo nginx -t` and if everything is ok, then apply with `sudo systemctl restart nginx`.

Finally, we need to add your user to a apecial group to avoid issues with serving static files, so execute `sudo gpasswd -a www-data [your username]` with your own username then `sudo nginx -s reload` to fix the issue.

## Get and enable your SSL certificate to get HTTPS

The last step will be to use an SSL certificate for the website to be secure. We will here obtain a certificate from Let's Encrypt.

First obtain your certificate by executing `sudo certbot --nginx -d [your domain]` with your own domain or subdomain. When prompted, enter your personal email address, accept the conditions, choose wether or not you want to receive promotional emails, and say yes if you're asked whether or not to redirect the HTTP traffic to HTTPS.

The certificate should automatically be loaded in your server and the Nginx config will automatically be edited too. The certificate will automatically be renewed when necessary.

## You're now all set!

Open your web browser and enter your domain, and you should get the ShortView index page!

If you need to update the project, you can stash the current files, then pull the changes, and then get bach the local files, and eventually handle conflicts, with this set of commands:

```bash
git stash
git pull
git stash pop
```

Then run `sudo systemctl restart shortview` to reload the project.
