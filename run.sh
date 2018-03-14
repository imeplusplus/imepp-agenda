#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/venv/bin/activate
source $DIR/.ENV

cd $DIR

./bot.py --noauth_local_webserver
