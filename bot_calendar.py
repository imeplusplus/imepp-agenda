from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import dateutil.parser

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'imepp-agenda'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'calendar-python.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            flow.user_agent = APPLICATION_NAME
        print('Storing credentials to ' + credential_path)
    return credentials

def hm(delta):
    s = delta.seconds
    return (s//3600, (s//60)%60)

def get_best_format(start, end):
    now = datetime.datetime.now()
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)
    now = now.replace(tzinfo=None)

    if(start < now and now < end):
        return "está acontencendo agora"
    if(now > end):
        return "acabou =[, até a próxima"

    diff = start - now
    day = datetime.timedelta(1)
    if(diff > day):
        return start.strftime("%d/%m (%a), %H:%Mh ~ ") + end.strftime("%H:%Mh")

    diff_h, diff_m = hm(diff)
    return "Em {} horas e {} min".format(diff_h, diff_m)


def get_events(n):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z';

    message = '<strong>IME++ Eventos</strong>\n\n'
    eventsResult = service.events().list(
        calendarId='o0bkduioq07c76n27lrgb37ilc@group.calendar.google.com',
        timeMin=now, maxResults=n, singleEvents=True, orderBy='startTime').execute()
    events = eventsResult.get('items',[])

    if not events:
        return 'Não temos nenhum evento marcado =['
    for event in events:
        start = dateutil.parser.parse(event['start'].get('dateTime', event['start'].get('date')))
        end = dateutil.parser.parse(event['end'].get('dateTime', event['start'].get('date')))
        s = get_best_format(start, end)

        message = message + event['summary'] + ':\n'
        message = message + s + '\n\n'

    return message
