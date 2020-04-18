import os
import sys
import psycopg2
import urllib.parse as urlparse
import random

from pyquery import PyQuery as pq
from slacker import Slacker

sys.path.append(os.path.abspath(os.curdir))

from slackbot_settings import API_TOKEN


if __name__ == '__main__':
    slack = Slacker(API_TOKEN)
    name1 = os.environ.get('NAME1', None)
    name2 = os.environ.get('NAME2', None)

    message = '今日のお風呂掃除は{}です'.format(random.choice([name1, name2]))
    slack.chat.post_message('#general', message, as_user=True)
