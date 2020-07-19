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
import time
import re
import threading
from bs4 import BeautifulSoup
from Util import load, save


class MGLocalFetchBot:
    #[name, index, num]
    local_data = {}
    old = []
    newls = []

    @staticmethod
    def getAll(datasave=True):
        """
        return [index, time, num1, num1delta, num2, num2delta]
        """
        print('Local Data 수집 시작')

        MGLocalFetchBot.old = load('localdata.bin')
        #[url, num1, num2, index]
        bundle = [['https://www.suwon.go.kr/web/safesuwon/corona/PD_index.do#none', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > table > tbody > tr > td:nth-child(1)', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > table:nth-child(2) > tbody > tr > td:nth-child(2)', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > div'],
                  ['https://corona.seongnam.go.kr/', '#corona_page > div.corona_page_top > div > div.contents_all > div.pc_view > table > tbody > tr > td:nth-child(1) > b', '#corona_page > div.corona_page_top > div > div.contents_all > div.pc_view > table > tbody > tr > td:nth-child(3) > b', '#corona_page > div.corona_page_top > div > div.contents_all > span']]

        threads = []

        i = 0
        idx_ls = [0, 2]
        for data in bundle:
            threads.append(threading.Thread(
                target=MGLocalFetchBot.Fetch_local_case1, args=(data, idx_ls[i])))
            i += 1

        threads.append(threading.Thread(
            target=MGLocalFetchBot.Fetch_local_case2))

        threads.append(threading.Thread(
            target=MGLocalFetchBot.Fetch_local_case3))

        start = time.time()
        for x in threads:
            x.start()

        for x in threads:
            x.join()
        end = time.time()

        datals = []
        if datasave:
            numls = []
        print(MGLocalFetchBot.local_data)
        for k, v in sorted(MGLocalFetchBot.local_data.items()):
            datals.append(v)
            if datasave:
                if len(v) == 0:
                    numls.append(MGLocalFetchBot.old[k])
                else:
                    numls.append([v[2], v[4]])

        # print(numls)
        if datasave:
            MGLocalFetchBot.newls = numls

        print('Local Data 수집 끝', end-start)
        print(datals)
        return datals

    # [index, time, num1, num1delta, num2, num2delta]
    @staticmethod
    def Fetch_local_case1(data, idx):
        try:
            res = requests.get(data[0], timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            ni = soup.select(data[3])[0].text.split(',')
            num = int(soup.select_one(data[1]).text.replace('\r', '').replace(
                '\n', '').replace('\t', '').replace('명', ''))
            num2 = int(soup.select_one(data[2]).text.replace('명', ''))
            MGLocalFetchBot.local_data[idx] = [
                ni[0], ni[1].strip(' '), num, num-MGLocalFetchBot.old[idx][0], num2, num2-MGLocalFetchBot.old[idx][1]]
        except Exception as e:
            import traceback
            print(e)
            print(traceback.print_exc())
            MGLocalFetchBot.local_data[idx] = []

    @staticmethod
    def Fetch_local_case2():
        try:
            res = requests.post(
                'http://27.101.50.5/prog/stat/corona/json.do', timeout=5)
            datadict = res.json()
            index = datadict['status_date']
            m = re.search('(.+기준)', index)
            if m:
                index = m.group(1)
            num = datadict['item_1']
            num2 = num - datadict['item_5']
            MGLocalFetchBot.local_data[3] = [
                '천안시청', index, num, num-MGLocalFetchBot.old[3][0], num2, num2-MGLocalFetchBot.old[3][1]]
        except:
            MGLocalFetchBot.local_data[3] = []

    @staticmethod
    def Fetch_local_case3():
        res = requests.get('http://www.yongin.go.kr/health/ictsd/index.do')
        soup = BeautifulSoup(res.text, 'html.parser')
        num2 = int(soup.select_one(
            '#coronabox_1 > div.coronacon_le > div > div:nth-child(1) > div.tbl_st1.tbl_corona.tbl_corona2 > table > tbody > tr > td:nth-child(1) > b > span').text)
        niso = int(soup.select_one(
            '#coronabox_1 > div.coronacon_le > div > div:nth-child(1) > div.tbl_st1.tbl_corona.tbl_corona2 > table > tbody > tr > td:nth-child(2) > b > span').text)
        num = num2+niso
        ni = soup.select_one(
            '#coronabox_1 > div.coronacon_le > div > div:nth-child(1) > h4 > span').text.split(',')

        MGLocalFetchBot.local_data[1] = [
            ni[0], ni[1], num, num-MGLocalFetchBot.old[1][0], num2, num2-MGLocalFetchBot.old[1][1]]

    @staticmethod
    def save_newls():
        save(MGLocalFetchBot.newls, 'localdata.bin')
