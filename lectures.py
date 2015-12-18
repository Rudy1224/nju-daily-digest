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
titles = re.findall('title:\'(.*?)\'', r.text)
temp = list(zip(titles, brds, files))

url_base = '<a href="http://bbs.nju.edu.cn/bbstcon?board={}&file={}">{}</a>'
res = [url_base.format(t[1], t[2], t[0]) for t in temp]

text = '\n<br><br>'.join(res)
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