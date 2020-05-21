"""
MIT License

Copyright (c) 2020 Taehyeok Kang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
import time, re, threading
from bs4 import BeautifulSoup
from Util import load, save

class MGLocalFetchBot:
    #[name, index, num]
    local_data = {}
    old = []
    @staticmethod
    def getAll(datasave=True):
        print('Local Data 수집 시작')
        
        MGLocalFetchBot.old = load('localdata.bin')
        #[url, num, index]
        bundle = [['https://www.suwon.go.kr/web/safesuwon/corona/PD_index.do#none', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > table > tbody > tr > td:nth-child(1)', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > div'],
        ['http://www.yongin.go.kr/index.do', '#corona_top > div > ul > li:nth-child(1) > p', '#corona_top > div > p:nth-child(5)'],
        ['https://corona.seongnam.go.kr/', '#corona_page > div.corona_page_top > div > div.contents_all > div.pc_view > table > tbody > tr > td:nth-child(1)', '#corona_page > div.corona_page_top > div > div.contents_all > span']]
        
        threads = []

        i = 0
        for data in bundle:
            threads.append(threading.Thread(target=MGLocalFetchBot.Fetch_local_case1, args=(data, i)))
            i+=1

        threads.append(threading.Thread(target=MGLocalFetchBot.Fetch_local_case2))
        
        start = time.time()
        for x in threads:
            x.start()

        for x in threads:
            x.join()
        end = time.time()

        datals = []
        if datasave:
            numls = []
        for k, v in sorted(MGLocalFetchBot.local_data.items()):
            datals.append(v)
            if datasave:
                if len(v) == 0:
                    numls.append(MGLocalFetchBot.old[k])
                else:
                    numls.append(v[2])
        
        # print(numls)
        if datasave:
            save(numls, 'localdata.bin')
        
        print('Local Data 수집 끝', end-start)
        print(datals)
        return datals

    @staticmethod
    def Fetch_local_case1(data, idx):
        try:
            res = requests.get(data[0], timeout=3)
            soup = BeautifulSoup(res.text, 'html.parser')
            ni = soup.select(data[2])[0].text.split(',')
            num = int(soup.select(data[1])[0].text.replace('\r', '').replace('\n', '').replace('\t', '').replace('명', ''))
            MGLocalFetchBot.local_data[idx] = [ni[0], ni[1].strip(' '), num, num-MGLocalFetchBot.old[idx]]
        except:
            MGLocalFetchBot.local_data[idx] = []

    @staticmethod
    def Fetch_local_case2():
        try:
            res = requests.post('http://27.101.50.5/prog/stat/corona/json.do', timeout=3)
            datadict = res.json()
            index = datadict['status_date']
            m = re.search('(.+기준)', index)
            if m:
                index = m.group(1)
            num = datadict['item_1']
            MGLocalFetchBot.local_data[3] = ['천안시청', index, num, num-MGLocalFetchBot.old[3]]
        except:
            MGLocalFetchBot.local_data[3] = []