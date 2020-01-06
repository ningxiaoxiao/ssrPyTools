import sys
import os
import json
import csv
from urllib.request import urlretrieve


cards_json=json.load(open('ssrcards.json',encoding='utf8'))
xls = open('allcard.csv','w',newline='',encoding='utf-8-sig')
cw=csv.writer(xls)
#写标题
cw.writerow(['name','level','pic'])
for c in cards_json:
    # urlretrieve('https://ssr.res.netease.com/pc/zt/20191112204330/data/card/'+str(c['id'])+'.png', 'c:\\ssr\\'+str(c['id'])+'.png')
    try:
        
        cw.writerow([c['name'],'L:\ssrCG\image\cards\l'+str(c['stage'])+'.png','c:\\ssr\\'+str(c['id'])+'.png'])
        print(c['name'],c['stage'],c['id'])
    except :
        pass
    
xls.close()