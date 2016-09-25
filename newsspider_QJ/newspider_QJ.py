
import re
import urllib.request
import sys
import time
import json
import requests
from bs4 import BeautifulSoup

# 一些变量
newsapiurl = 'https://api.bmob.cn/1/classes/newslist'
tagapiurl = 'https://api.bmob.cn/1/batch'
headers = {
    "X-Bmob-Application-Id": "my application-id",
    "X-Bmob-REST-API-Key": "my rest-API-Key",
    "Content-Type": "application/json"
}
############################
# 查找最新一条新闻的地址
############################


# 驱家新闻URL
searchlatesturl = "http://news.mydrivers.com/"
# 发起请求
resp = urllib.request.urlopen(searchlatesturl).read().decode("gbk")
# 解析返回的结果
soup = BeautifulSoup(resp, "html.parser")
# 从列表中选中第一个，即最新的一条新闻，获取其链接
try:
    latestlink = soup.find("div", "news_box").a['href']
except Exception as e:
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    print(e)
    print()
    sys.exit(0)
# 找到新闻后三个数字id
latestidre = re.compile("(\d{3}).htm")
latestid = int(latestidre.findall(latestlink)[0])
#找到新闻的前三个id
latestnumre = re.compile("/(\d{3})/")
latestnum = int(latestnumre.findall(latestlink)[0])


############################
# 查找完毕
############################

############################
# 开始爬取新闻
############################

# 不断循环爬取
while True:
    # 一个部分爬取完成了，下一部分
    if latestid<0:
        latestid = 999
        latestnum -=1
    # 组合出完整的URLid
    urlid = str(latestnum).rjust(3, "0") + str(latestid).rjust(3, "0")
    # 合成新闻页完整的URL
    newsurl = "http://news.mydrivers.com/1/" + str(latestnum) + "/" + str(urlid) + ".htm"
    # 构造新闻的json
    newsjson = {}
    # 放入新闻URL
    newsjson['newsurl'] = newsurl
    # 发起请求，获取新闻页面
    try:
        newsresp = urllib.request.urlopen(newsurl).read().decode("gbk")
    except Exception as e:
        latestid -= 1
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(newsurl)
        print(e)
        print()
        time.sleep(3)
        continue
    # 解析新闻页面
    soup = BeautifulSoup(newsresp, "html.parser")
    # 获得新闻的标题
    newsjson['newstitle'] = soup.find(id="thread_subject").string
    # 获得新闻发布时间的div
    timediv = str(soup.find("div", "news_bt1_left"))
    # 获得新闻的发布时间
    publictimere = re.compile("(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
    publictime = {"__type": "Date"}
    publictime['iso'] = publictimere.findall(timediv)[0]
    newsjson['publictime'] = publictime
    newsinfo = soup.find("div", "news_info")

    # 获取一张图片作为封面
    try:
        newsjson['picsrc'] = newsinfo.find("img")["src"]
    except Exception as e:
        #没有图片的新闻……
        newsjson['picsrc'] = "http://icons.mydrivers.com/www/2014/v2/kkg.png"
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(newsurl)
    try:
        # 获取所有的p标签，即所有的新闻内容，去除最后三个广告
        plist = newsinfo.find_all("p")[:-3]
    except Exception as e:
        # 驱家评测的内容暂时不能解析
        latestid -= 1
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(newsurl)
        print(e)
        print()
        time.sleep(3)
        continue
    # 合成新闻内容和摘要
    newscontent = u""
    digest = u""
    for p in plist:
        try:
            newscontent += str(p)
            if len(digest)<20:
                digest += str(p.text)
        except:
            newscontent += "<br/>"
            continue
    newsjson['newscontent']=newscontent
    newsjson['digest']=digest[:20]
    #print(newsjson)
    #break
    # 把新闻发送到bmob
    try:
        apiresp = requests.post(newsapiurl, data=json.dumps(newsjson), headers=headers)
    except Exception as e:
        # 网络问题
        latestid -= 1
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(newsurl)
        print(e)
        print()
        time.sleep(3)
        continue
    # 发送失败
    if apiresp.status_code != 201:
        # 内容重复
        if apiresp.json()['code'] ==401:
            #print('重复内容！结束')
            sys.exit(0)
        # 其他情况
        latestid -= 1
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(apiresp.json())
        print()
        time.sleep(3)
        continue

    # 开始统计tag

    # 获得tag所在的div
    tagdiv = soup.find("span", "news_bq_list")
    # 找到所有的tag
    taglist = tagdiv.find_all("a")
    # 准备一个列表放置tag的请求体
    reqjsonlist = []
    # 循环构造tag的请求体
    for a in taglist:
        # 一个tag的请求体
        tagjsonbody = {}
        # 放入tag的新闻URL
        tagjsonbody['newsurl'] = newsurl
        # 放入新闻发布时间
        tagjsonbody['publictime'] = publictime
        # 放入标签
        tagjsonbody['tag'] = a.text
        # 形成一个tag的json
        tagjson = {
            "method": "POST",
            "path": "/1/classes/taglist"
        }
        tagjson['body'] = tagjsonbody
        # 形成一个请求列表
        reqjsonlist.append(tagjson)
    # 构造一个完整的请求
    reqjson = {}
    reqjson['requests'] = reqjsonlist
    # 发起请求
    try:
        reqapi = requests.post(tagapiurl, headers=headers, data=json.dumps(reqjson))
    except Exception as e:
        # 网络问题请求失败
        latestid -= 1
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(newsurl)
        print(e)
        print()
        time.sleep(3)
        continue
    #else:
    #    print(newsjson['newstitle'])
    # 下一条新闻
    latestid -= 1
    time.sleep(3)