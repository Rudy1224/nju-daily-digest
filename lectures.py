import re
import time
import json
import requests
import configparser
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL

# read configurations
config = configparser.ConfigParser()
config.read('account.ini')
SMTP_SERVER = config['lectures.py']['server']
SMTP_PORT = config['lectures.py']['port']
FROM_ADDR = config['lectures.py']['from']
PASSWD = config['lectures.py']['passwd']
TO_ADDR = config['lectures.py']['to']
API_TOKEN = config['lectures.py']['api_token']

# get lecture list
r = requests.get('http://bbs.nju.edu.cn/cache/t_act.js')
r.encoding = 'gb2312'
brds = re.findall('brd:\'(.*?)\'', r.text)
files = re.findall('file:\'(.*?)\'', r.text)
temp = list(zip(brds, files))

titles = ['<h3>{}</h3>'.format(t) for t in re.findall('title:\'(.*?)\'', r.text)]
urls = ['http://bbs.nju.edu.cn/bbstcon?board={}&file={}'.format(t[0], t[1]) for t in temp]
hrefs = ['...<br><a href="http://bbs.nju.edu.cn/bbstcon?board={}&file={}"><i>>>>传送门<<<</i></a><br>'.format(t[0], t[1]) for t in temp]


def parse_content(urls):
    # get detailed content of the lecture
    # only the first image (if any) will be added to the email
    IMG = re.compile(r'(http.*?\.(?:bmp|jpg|jpeg|png|tiff|gif|ico))')
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
            # check if images place outside the first 8 lines
            # note that only the first image will be added to the final email if multiple images exist
            img=re.sub(IMG,r'<br><img src="\1"></img>', img_in_remain[0])
            res.append(first_8_lines+img)
        else:
            res.append(first_8_lines)
    return res


def query_aqi():
    # get air quality information using api provided by pm25.in
    aqi_detail = requests.get('http://pm25.in/api/querys/aqis_by_station.json',
                              params={'station_code': '1159A', 'token': API_TOKEN}).json()

    if 'error' in aqi_detail:
        return aqi_detail['error']
    else:
        return '<i>空气质量</i>：{}，'\
               '<i>主要污染物</i>：{}，'\
               '<i>AQI</i>：{}，'\
               '<i>实时PM<sub>2.5</sub></i>：{}，'\
               '<i>24小时PM<sub>2.5</sub></i>：{}'.\
            format(
                aqi_detail[0]['quality'],
                aqi_detail[0]['primary_pollutant'],
                aqi_detail[0]['aqi'],
                aqi_detail[0]['pm2_5'],
                aqi_detail[0]['pm2_5_24h'])


def query_weather():
    # get weather information
    weather_detail = requests.get('http://d1.weather.com.cn/sk_2d/101190101.html',
                                  params={'_':1451577174497},
                                  headers={'Referer': 'http://m.weather.com.cn/mweather/101190101.shtml'})
    weather_detail.encoding = 'utf8'
    try:
        w = json.loads(weather_detail.text[13:])
        return '<i>当前天气</i>：{}，'\
               '<i>温度</i>：{}&#8451;，'\
               '{}，'\
               '<i>湿度</i>：{}'.\
            format(
                w['weather'],
                w['temp'],
                w['WD']+w['WS'],
                w['sd'])
    except:
        return ''

text = query_weather()+'\n<br>'+query_aqi()+'\n<br><br>'
text += '\n<br>'.join(''.join(item) for item in zip(titles, parse_content(urls), hrefs))
# print(text)

msg = MIMEText(text, _subtype='html')
msg['To'] = TO_ADDR
fromhdr = Header('nju-daily-digest')
fromhdr.append('<{}>'.format(FROM_ADDR))
msg['From'] = fromhdr
msg['Subject'] = "各类活动与讲座预告({})".format(time.strftime('%Y-%m-%d', time.localtime(time.time())))

s = SMTP_SSL(host=SMTP_SERVER, port=SMTP_PORT)
s.login(FROM_ADDR, PASSWD)
s.sendmail(FROM_ADDR, TO_ADDR, msg.as_bytes())
s.close()