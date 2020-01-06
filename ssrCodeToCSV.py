# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import sys
import os
import re
import execjs
import time
import json
import base64
import csv
import urllib
import requests
import logging
from requests.packages import urllib3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# 关掉ssl警告
urllib3.disable_warnings()
#使用log
log=logging.getLogger()
log.setLevel(logging.INFO)
sh=logging.StreamHandler()
log.addHandler(sh)

# 官方全卡组
cards = {}
allcards = json.load(open('ssrcards.json', encoding='utf8'))
for c in allcards:
    cards[c['id']] = c

# 官网的登录态
token = ''
try:
    # 尝试从文件中读出上次的key,如果有
    with open('ssrtoken.key', 'r') as fr:
        token = fr.read()
except:
    pass


m_user = 'ningxiaoxiao1991@163.com'
m_pw = '1q2w3e4r'
# cookies 持久化
http = requests.Session()


def getToken():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)  # 等待的最大时间
    driver.get('https://ssr.163.com/cardmaker/#/')
    login_btn = driver.find_element_by_xpath('/html/body/div[3]/div[2]/a')
    login_btn.click()

    # 切换frame
    frame = wait.until(EC.presence_of_element_located((By.XPATH, '//iframe')))

    driver.switch_to_frame(frame)
    # 写用户名与密码

    input_name = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
    input_pw = driver.find_element_by_name("password")

    input_name.send_keys('ningxiaoxiao1991@163.com')
    input_pw.send_keys('1q2w3e')
    ok_btn = driver.find_element_by_xpath('//*[@id="dologin"]')
    # 点击登录
    ok_btn.click()
    # 等到出现退出登录
    driver.switch_to_default_content()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'exit-btn')))
    # 要去别的页面
    driver.get('https://interact2.webapp.163.com/g97simulate/urs/login')
    html = driver.find_element_by_xpath("//*").get_attribute("innerText")

    # 得到token
    j = json.loads(html)
    
    driver.quit()
    key = j['weixin_token']
    print('update token:', key)
    # 写出去
    with open('ssrtoken.key', 'w') as fw:
        fw.write(key)
    return key


def login(file='login.js'):
    pd = "game"
    js = execjs.compile(open(file, 'r+', encoding='utf-8').read())
    topURL = "https%3A%2F%2Fssr.163.com%2Fcardmaker%2F%23%2F"
    rtid = js.call('getRtid')
    pkid = "AGyReXQ"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Host': 'dl.reg.163.com',
        'Referer':
            f'https://dl.reg.163.com/webzj/v1.0.1/pub/index_dl2_new.html?cd=https%3A&cf=%2F%2Fssr.res.netease.com%2Fpc%2Fzt%2F20191112204330%2Flogin.css%2C%2F%2Fnie.res.netease.com%2Fcomm%2Fjs%2Fnie%2Futil%2Flogin2%2Fcss%2Flogin2-unit-1_6ec927f.css&'
            f'MGID={round(time.time() * 1000, 4)}&wdaId=&pkid={pkid}&product=game'
    }
    url = f'https://dl.reg.163.com/dl/getConf?pkid={pkid}&pd={pd}&mode=1'
    res = http.get(url, headers=headers, verify=False)

    url = f'https://dl.reg.163.com/dl/ini?pd={pd}&pkid={pkid}&pkht=game.163.com&channel=0&' \
        f'topURL={topURL}&rtid={rtid}&nocache={int(time.time() * 1000)}'
    res = http.get(url, headers=headers, verify=False)

    print('ini-step-1:', res.content)

    print('cookies:', res.cookies)
    # 得到TK
    url = f'https://dl.reg.163.com/dl/gt?un={urllib.parse.quote(m_user)}&pkid={pkid}&pd={pd}&channel=0&' \
        f'topURL={topURL}&rtid={rtid}&nocache={int(time.time() * 1000)}'
    res = http.get(url, headers=headers,  verify=False)

    res = res.json()
    global token
    token = res.get('tk', '')
    print('tk:', res)
    # 登录
    url = 'https://dl.reg.163.com/dl/l'
    data = {
        "un": m_user,
        "pw": js.call('getPw', m_pw),
        "pd": pd,
        "l": 0,
        "d": 10,
        "t": int(time.time() * 1000),
        "pkid": pkid,
        "domains": "",
        "tk": res.get('tk', ''),
        "pwdKeyUp": 1,
        "channel": 0,
        "topURL": topURL,
        "rtid": rtid
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Origin': 'dl.reg.163.com',
        'Referer': headers.get('Referer'),
    }

    res = requests.post(url, headers=headers,
                        data=json.dumps(data), verify=False)

    print('login:', res.content)
    url = f'https://interact2.webapp.163.com/g97simulate/urs/login?_={int(time.time() * 1000)}'
    res = http.get(url, headers=headers, verify=False)
    print(json.loads(res.content.decode('utf8')))

# 从网站得数据


def getCards(code):
    global token
    data = {
        "token": token,
        "user_id": '463',
        "extra": code,
    }

    # postdata = urllib.parse.urlencode(data).encode('utf-8')
    jtext = requests.post("https://interact2.webapp.163.com/g97simulate/resolve_card",
                          data=data)

    res = jtext.json()

    if 'ddcards' in str(res):
        # print('返回正常:', res)
        return res

    print('要刷新token:', res)
    # 刷新token
    token = getToken()
    return getCards(code)


def id2name(id):
    return cards[int(id)]['name']


def code2row(code):
    # 前四个是式神名,后32个是卡名,一一对应
    cj = getCards(code)['ddcards']
    cardlist = []
    for c in cj:
        # 取卡 如果是2张,就生成2个数字
        for x in range(int(c[1])):
            cardlist.append((c[0]))
    # 卡排序
    cardlist.sort()
    temp = []
    sslist = []
    for c in cardlist:
        # 取式神
        sslist.append(str(c)[0:3]+'00')
        # 取出卡
        temp.append(id2name(c))
    cardlist = temp
    # 式神去重
    sslist = list(set(sslist))
    # 排序 一定要排序一次,去重会把数据弄乱
    sslist.sort()
    # print('式神代码 排序后', sslist)
    # print(cardlist)
    # 拼接
    row = []
    for ss in sslist:
        row.append(id2name(ss))
    row.extend(cardlist)
    if len(row) !=36:
        print('err')
        logging.error('数量不对:'+str(len(row)))
        
    return row


def createPlayerCards():
    # 目标文件
    
    xls = csv.writer(open('playercards.csv', 'w', newline='', encoding='utf-8-sig'))
    # 选手信息
    playerxls = csv.reader(open('player.csv', encoding='utf8'),)
    # name rank code1 code2 code3
    # 制作标题
    title = ['name', 'rank']
    for x in range(4):
        title.append('ss'+str(x))
    for x in range(32):
        title.append('c'+str(x))
    # 写出标题
    xls.writerow(title)
    next(playerxls)  # 跳过第一行标题
    for p in playerxls:
        for x in range(4, 7):
            row = [p[0], p[1]]
            row.extend(code2row(p[x]))
            # print(row)
            log.info(row)
            xls.writerow(row)

  
def createPlayinfo():
    #读取选手
    playerxls=csv.reader(open('player.csv',encoding='utf8'))
    #name rank code1 code2 code3
    xls=csv.writer(open('playerinfo.csv','w',newline='',encoding='utf-8-sig'))
    #制作标题
    title=['游戏名称','最高段位','胜场','天梯最高排名']
    for x in range(4):
        for y in range(4):
            title.append('ss'+str(x)+str(y))
    #写出标题
    xls.writerow(title)
    next(playerxls)#跳过第一行
    for p in playerxls:
        row=[p[0],p[1],p[2],p[3]]
        for x in range(4,7):
            #只使用前四个
            row.extend(code2row(p[x])[:3])
        print(row)
        xls.writerow(row)    

createPlayinfo()