# Cloning repository

Clone repository to `/src/imepp-agenda`

# Configuring Server

## Language locale

Install `pt_BR.utf8` (or change `bot.py` to your `locale`)

```
$ sudo apt install language-pack-pt
$ sudo dpkg-reconfigure locales
```

## Set time

[Reference](https://www.digitalocean.com/community/tutorials/how-to-set-up-time-synchronization-on-ubuntu-16-04)

Set timezone to `America/Sao_Paulo`

```
$ sudo timedatectl set-timezone America/Sao_Paulo
```

# Configuring IMEppAgenda

## Python3, virtualenv and pip

Install python3, virtualenv and pip

```
$ sudo apt install python3 python3-pip python3-venv
```

Run virtualenv

```
$ python3 -m venv venv
$ . ./venv/bin/activate
```

(To deactivate virtualenv just run `deactivate`)

## Install requirements

```
$ pip install -r requirements.txt
```

## Setup database

```
$ bash setup.sh
```

## Install service

Copy `imepp-agenda.service` to `/etc/systemd/system`.

Enable it to run at boot:

```
$ sudo systemctl start imepp-agenda
```

## Configure TOKEN

Get your bot `TOKEN` using [BotFather](https://telegram.me/BotFather).

Create a file `.ENV` to store your token

```
$ echo TOKEN=YOUR_TOKEN_HERE > .ENV
```

# Run the bot

Having configured everything, the bot should run as a service

```
$ sudo systemctl start imepp-agenda
```
