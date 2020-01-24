import os
import sys
import psycopg2
import urllib.parse as urlparse

from pyquery import PyQuery as pq
from slacker import Slacker

sys.path.append(os.path.abspath(os.curdir))

from slackbot_settings import API_TOKEN


def dokkaiahen():
    base_url = 'http://dka-hero.com/'

    page = pq(url=base_url + 't_m.html', encoding='shift_jis')  # 左の
    horimiya_pq = page("center").eq(1)("table").eq(1)("tr").eq(1)("td").eq(1)("a")
    horimiya = horimiya_pq.text()
    aco_pq = page("center").eq(1)("table").eq(1)("tr").eq(4)("td").eq(1)("a")
    aco = aco_pq.text()

    page2 = pq(url=base_url + 'mat/new.html', encoding='shift_jis') # 更新履歴
    others_pq = page2("td").eq(0)
    others = others_pq.text()[:4]  # 日付

    data_url = urlparse.urlparse(os.environ['DATABASE_URL'])
    conn = psycopg2.connect(
        dbname = data_url.path[1:],
        user = data_url.username,
        password = data_url.password,
        host = data_url.hostname,
        port = data_url.port
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM horimiya")
    horimiya_old = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM aco")
    aco_old = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM others")
    others_old = cursor.fetchone()[0]

    flag = True
    new = []
    if horimiya != horimiya_old:
        cursor.execute("UPDATE horimiya SET title = " + repr(horimiya))
        new.append({'title': horimiya, 'link': base_url + horimiya_pq.attr('href')})
        flag = False

    if aco != aco_old:
        cursor.execute("UPDATE aco SET title = " + repr(aco))
        new.append({'title': aco, 'link': base_url + aco_pq.attr('href')})
        flag = False

    if others != others_old:
        cursor.execute("UPDATE others SET title = " + repr(others))
        new.append({'title': others, 'link': base_url + "top.html"})
        flag = False

    if flag:
        print('There is no update on {}'.format(base_url))

    conn.commit()
    cursor.close()
    conn.close()

    return new

if __name__ == '__main__':
    slack = Slacker(API_TOKEN)
    new = dokkaiahen()
    if new:
        message = '読解アヘンに更新があります\n'
        for res in new:
            message += '{title}: {link}\n'.format(**res)
        slack.chat.post_message('#general', message, as_user=True)
