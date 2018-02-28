# Configure

## Language locale

Install `pt_BR.utf8` (or change `bot.py` to your `locale`)

```
$ sudo apt install language-pack-pt
$ sudo dpkg-reconfigure locales
```

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

# Run

Get your bot `TOKEN` using [BotFather](https://telegram.me/BotFather).

Run the bot using:

```
$ TOKEN=YOUR_TOKEN_HERE ./bot.py
```
