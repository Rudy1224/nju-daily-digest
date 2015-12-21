import re
import time
import requests
import configparser
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

config = configparser.ConfigParser()
config.read('account.ini')
smtpServer = config['lectures.py']['server']
fromAddr = config['lectures.py']['from']
passwd = config['lectures.py']['passwd']
toAddr = config['lectures.py']['to']

r = requests.get('http://bbs.nju.edu.cn/cache/t_act.js')
r.encoding = 'gb2312'
brds = re.findall('brd:\'(.*?)\'', r.text)
files = re.findall('file:\'(.*?)\'', r.text)
temp = list(zip(brds, files))

titles = ['<h3>{}</h3>'.format(t) for t in re.findall('title:\'(.*?)\'', r.text)]
urls = ['http://bbs.nju.edu.cn/bbstcon?board={}&file={}'.format(t[0], t[1]) for t in temp]
hrefs = ['...<br><a href="http://bbs.nju.edu.cn/bbstcon?board={}&file={}"><i>>>>传送门<<<</i></a><br>'.format(t[0], t[1]) for t in temp]


def parse_content(urls):
    IMG = re.compile(r'(http.*\.(?:bmp|jpg|jpeg|png|tiff|gif|ico))')
    res = []
    for url in urls:
        s = requests.get(url)
        first_8_lines = '\n<br>'.join(s.text.splitlines()[12:20])
        remaining_lines = ''.join(s.text.splitlines()[20:])
        img_in_first = re.findall(IMG, first_8_lines)
        img_in_remain = re.findall(IMG, remaining_lines)

        if img_in_first:
            res.append(re.sub(IMG,r'<br><img src="\1"></img>', first_8_lines))
        elif img_in_remain:
            img=re.sub(IMG,r'<br><img src="\1"></img>', img_in_remain[0])
            res.append(first_8_lines+img)
        else:
            res.append(first_8_lines)
    return res

text = '\n<br><br>'.join('\n<br>'.join(item) for item in zip(titles, parse_content(urls), hrefs))
# print(text)
msg = MIMEText(text, _subtype='html')
msg['To'] = toAddr
fromhdr = Header('小迪')
fromhdr.append('<{}>'.format(fromAddr))
msg['From'] = fromhdr
msg['Subject'] = "各类活动与讲座预告({})".format(time.strftime('%Y-%m-%d', time.localtime(time.time())))

s = SMTP_SSL(host=smtpServer, port=465)
s.login(fromAddr, passwd)
s.sendmail(fromAddr, toAddr, msg.as_bytes())
s.close()