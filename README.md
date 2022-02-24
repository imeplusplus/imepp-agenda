# Cloning repository

Clone repository to `/src/imepp-agenda`

# Configuring Server

## Language locale

Install `pt_BR.utf8` (or change `bot.py` to your `locale`)

(This may not be required (wasn't on Raspbian): `$ sudo apt install language-pack-pt`)

```
$ sudo dpkg-reconfigure locales
```

## Set time

[Reference](https://www.digitalocean.com/community/tutorials/how-to-set-up-time-synchronization-on-ubuntu-16-04)

Set timezone to `America/Sao_Paulo`

```
$ sudo timedatectl set-timezone America/Sao_Paulo
```

# Downloading dependencies

```
$ sudo apt install python3 python3-pip python3-venv
```

# Configuring IMEppAgenda

## Create user and setup folders

```
$ sudo adduser imeppagenda
$ sudo su imeppagenda
$ cd
$ git clone <this-repo>
$ cd imepp-agenda
```

## Python3, virtualenv and pip

Run virtualenv

```
$ python3 -m venv venv
$ source venv/bin/activate
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

# Setup Google Calendar

1. Sign-in as `IME++` on Google
2. Enter [https://console.developers.google.com/apis/credentials](Google API Credentials)
3. Download JSON
4. Rename to `credentials.json`

## Install service

Link `imepp-agenda.service` to `/etc/systemd/system`.

```
$ sudo ln -s /home/imeppagenda/imepp-agenda/imepp-agenda.service /etc/systemd/system/imepp-agenda.service
```

Enable it to run at boot:

```
$ sudo systemctl enable imepp-agenda
```

## Configure TOKEN

Get your bot `TOKEN` using [BotFather](https://telegram.me/BotFather).

Create a file `.ENV` to store your token

```
$ echo "export TOKEN=<YOUR_TOKEN_HERE>" > .ENV
```

# Run the bot

Having configured everything, the bot should run as a service

(Almost... You must run as `sudo` user first, since the authentication of Google
 Calendar must be configured by hand: `$ sudo ./run.sh`, and on Telegram type: `/events`)

```
$ sudo systemctl start imepp-agenda
```
