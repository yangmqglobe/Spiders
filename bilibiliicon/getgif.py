import requests
r = requests.get('http://www.bilibili.com/index/index-icon.json')
for icon in r.json()['fix']:
    print(icon['title'])
    print(icon['icon'])
    r = requests.get(icon['icon'])
    pic = open('icon/'+icon['title']+'.gif','wb')
    pic.write(r.content)
    pic.close()
print("完成！")