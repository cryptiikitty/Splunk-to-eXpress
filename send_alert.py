#!/usr/bin/python


import sys
import base64
import hashlib
import hmac
import logging
import time
from datetime import datetime

import json
import requests
import gzip
import re



# Bot ID and URLs
bot_id = ''
bot_url = ''
secret = ""
sendto = ""



def get_token():
    token_url = '/api/v2/botx/bots/' + bot_id + '/token'
    h = hmac.new(secret.encode('utf-8'), bot_id.encode('utf-8'), hashlib.sha256)
    signature = base64.b16encode(h.digest())
    r = requests.get(bot_url + token_url, params={'signature': signature})
    return r.json()['result']


# API authorization
token = get_token()
if token:
    headers = {
        'authorization': 'Bearer ' + token,
        'content-type': 'application/json'
    }
else:
    logging.info(timestamp, 'token not received', token)

# Message URL
msg_url = '/api/v3/botx/notification/callback/direct'


# Main function for sending messages to chat
def send_express(subject, message, link):
    button = '[Splunk search query]'
    url = '(' + link + ')'
    info = (message[:1050] + '\n ❗View all the results in Splunk❗') if len(message) > 1100 else message
    msg = "{}\n{}\n\n{}{}".format(subject, info, button, url)


    data = {
        "group_chat_id": sendto,
        "notification": {
            "status": "ok",
            "body": msg,

        }
    }


    try:
        requests.post(bot_url + msg_url, headers=headers, data=json.dumps(data))

    except Exception as ex:
        logging.info(repr(ex))


subj = sys.argv[4]
lnk = sys.argv[6]

# Read data about the issue from the file
with gzip.open(sys.argv[8], 'rt') as f:
    file_content = f.read().splitlines()
# Remove unnecessary fields from the header
match = re.match(r'(.*?)(,"__.*)', file_content[0])
file_new = match.group(1)
file_new = file_new.replace('"', '')

file_content.pop(0)
file_content.insert(0, file_new)


mess = []
for text in file_content:
    # alltext = ('\t'.join(text.split(',')))

    try:
        if text[0] == '"':
            text = text[1:]
        if text[0] == ',':
            text = text[1:]
        mess.append(text)
    except:
        print('error found')


f.close()
del mess[0]

if __name__ == '__main__':
    send_express(subj, ('\n'.join(mess)), lnk)
