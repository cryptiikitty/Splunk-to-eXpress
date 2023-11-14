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
msg_url = '/api/v4/botx/notifications/direct'


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


def send_express_with_mentions(subject, message, link, responsible_list):
    button = '[Splunk search query]' + '(' + link + ')'
    info = (message[:1050] + '\n ❗View all the results in Splunk❗') if len(message) > 1100 else message
    split = '----------------------------'
    responsible = ''
    for i in responsible_list:
        usr = '@{mention:' + i + '} '   # @{mention:id}
        responsible += '\n' + usr

    msg = "{}\n{}\n\n{}\n{}{}".format(subject, info, button, split, responsible)

    data = ''
    if len(responsible_list) == 1:
        data = {
            "group_chat_id": sendto,
            "notification": {
                "body": msg,
                "mentions": [
                    {
                        "mention_type": "user",
                        "mention_id": responsible_list[0],
                        "mention_data": {
                            "user_huid": responsible_list[0]
                        }
                    }
                ]
            }
        }
    elif len(responsible_list) == 2:
        data = {
            "group_chat_id": sendto,
            "notification": {
                "body": msg,
                "mentions": [
                    {
                        "mention_type": "user",
                        "mention_id": responsible_list[0],
                        "mention_data": {
                            "user_huid": responsible_list[0]
                        }
                    },
                    {
                        "mention_type": "user",
                        "mention_id": responsible_list[1],
                        "mention_data": {
                            "user_huid": responsible_list[1]
                        }
                    }
                ]
            }
        }
    else:
        data = {
            "group_chat_id": sendto,
            "notification": {
                "body": msg,
                "mentions": [
                    {
                        "mention_type": "user",
                        "mention_id": responsible_list[0],
                        "mention_data": {
                            "user_huid": responsible_list[0]
                        }
                    },
                    {
                        "mention_type": "user",
                        "mention_id": responsible_list[1],
                        "mention_data": {
                            "user_huid": responsible_list[1]
                        }
                    },
                    {
                        "mention_type": "user",
                        "mention_id": responsible_list[2],
                        "mention_data": {
                            "user_huid": responsible_list[2]
                        }
                    }
                ]
            }
        }

    try:
        r = requests.post(bot_url + msg_url, headers=headers, data=json.dumps(data))


    except Exception as ex:
        print('err')


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
file_content.pop(0)
file_content.insert(0, file_new)


mess = []
for text in file_content:
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


# Processing data for mentions
responsible_list = []

for element in mess[:]:
    if element.startswith("responsible: "):
        names_str = element.split("responsible: ")[1]
        names = [name.strip() for name in re.split(",\s*|\s+", names_str)]
        responsible_list += names
        mess.remove(element)


# Removing duplicates
resp_list = []
if responsible_list:
    responsible_list = sorted(list(set(responsible_list)))
    for i in responsible_list:
        if i[-1] == '"':
            i = i[:-1]
            resp_list.append(i)
        else:
            resp_list.append(i)


if __name__ == '__main__':
    if resp_list:
        send_express_with_mentions(subj, ('\n'.join(mess)), lnk, resp_list)
    else:
        send_express(subj, ('\n'.join(mess)), lnk)