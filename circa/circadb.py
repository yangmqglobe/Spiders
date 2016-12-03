# -*- coding:utf-8 -*-
"""
@author: yangmqglobe
@file: circadb.py
@time: 2016/12/3
"""
from bs4 import BeautifulSoup
from collections import deque
import requests
import linecache
import time

data = {
    'utf8': '✓',
    'authenticity_token': 'qnkQ1k8ZHGlMrsr0Kg4ejPpc7HCGXTgwu1qegV638xCxFFP24uOStYf/EokVxE6YGNpO5sG8j432Sy1LjCKoHA==',
    'query_string': '',
    'match_mode': 'gene_symbol',
    'query[filter]': 'jtk_q_value',
    'filter_value': '0.05',
    'phase_range': '0-40',
    'output_mode': 'slim',
    'number_entries0': '0',
    # 'assays[]': 1,
    'commit': 'Search',
    # 'page': 1
}
organ = 'organ.txt'
for i in range(2, 15):
    filename = linecache.getline(organ, i).rstrip()
    file = open('data/'+filename, 'wb')
    pages = deque(x for x in range(1, 51))
    errornum = 0
    done = False
    print(filename)
    while pages:
        try:
            time.sleep(3)
            page = pages.popleft()
            if done:
                page = pages.pop()
                errornum -= 1
            data['assays[]'] = i
            data['page'] = page
            print('\t'+str(page))
            r = requests.get('http://circadb.hogeneschlab.org/query', data, timeout=3)
            soup = BeautifulSoup(r.text, 'lxml')
            trs = soup.find_all('tr')
            if len(trs) == 0:
                done = True
            if errornum == 0 and done:
                break
            for k in range(1, len(trs) + 1, 2):
                genes = trs[k].find_all('td')[3].find_all('a')
                for gene in genes:
                    file.write((gene.string+'\n').encode())
                    file.flush()
                    # print('\t'*2+gene.string)
        except:
            if done:
                pages.appendleft(page)
            else:
                pages.append(page)
            errornum += 1
            print('error:'+str(page))
            continue
print('done!')
