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
from bs4 import BeautifulSoup
import time
import random
import sys
import re

from Util import *
from PIPELINES import PipeLine1, PipeLine2, PipeLine3, PipeLine6
       
class FetchBot:
    def __init__(self):
        if not len(sys.argv) == 1:
            # self.line5 = PipeLine5()
            self.middle = True
        else:
            self.lines = [PipeLine1(), PipeLine2(), PipeLine3(), PipeLine6()]
            # self.line4 = PipeLine4()
            self.middle = False

    def get_local_data(self):
        #[url, num, index]
        bundle = [['https://www.suwon.go.kr/web/safesuwon/corona/PD_index.do#none', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > table > tbody > tr > td:nth-child(1)', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > div'],
        ['http://www.yongin.go.kr/health/ictsd/index.do', '#coronabox_1 > div.coronacon_le > div > div:nth-child(1) > div > table > tbody > tr:nth-child(1) > td > b', '#coronabox_1 > div.coronacon_le > div > div:nth-child(1) > h4 > span'],
        ['http://www.seongnam.go.kr/coronaIndex.html', '#corona_page > div.corona_page_top > div > div.contents_all > ul > li:nth-child(2) > p', '#corona_page > div.corona_page_top > div > div.contents_all > span']]
        
        #[name, index, num]
        local_data = []
 
        for data in bundle:
            try:
                res = requests.get(data[0])
                soup = BeautifulSoup(res.text, 'html.parser')
                ni = soup.select(data[2])[0].text.split(',')
                local_data.append([ni[0], ni[1].strip(' '), soup.select(data[1])[0].text.replace('\r', '').replace('\n', '').replace('\t', '')])
            except:
                local_data.append([])
        try:
            res = requests.post('http://27.101.50.5/prog/stat/corona/json.do')
            datadict = res.json()
            index = datadict['status_date']
            m = re.search('(.+기준)', index)
            if m:
                index = m.group(1)
            local_data.append(['천안시청', index, str(datadict['item_1'])+'명'])
        except:
            local_data.append([])

        return local_data

    def get_world_data(self, num):
        x = requests.get('https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=200&cacheHint=true')
        data_dict = x.json()

        world_data = []

        for i in range(num):
            last = int(data_dict['features'][i]['attributes']['Last_Update']/1000)
            last_str = 'KST '+time.strftime('%m.%d %H:%M', time.localtime(last))+' 기준'
            country_data = [data_dict['features'][i]['attributes']['Country_Region'], last_str, data_dict['features'][i]['attributes']['Confirmed']]
            world_data.append(country_data)

        return world_data

    def run(self):
        if self.middle:
            sendtoBot_card(edit2_json(self.get_local_data(), self.get_world_data(10)))
        else:
            sendError('정보 수집 시작! 2')
            while True:
                for line in self.lines:
                    if len(self.lines) == 0:
                        sendError('모든 PIPELINE에서 오류가 발견되어 종료되었습니다.')
                        return
                    try:
                        check = line.run()
                    except:
                        sendError("PIPELINE "+line.id+'에서 오류가 발견되어 삭제합니다.')
                        self.lines.remove(line)
                        continue
                    print(line.id+' 업데이트 체크 중...')
                    if check:
                        print(line.id+' 업데이트 확인됨.')
                        data = line.get_data()                        
                        sendtoBot_card(edit1_json(data, line.id, self.get_local_data(), self.get_world_data(8)))
                        line.save_data()
                        return
                    time.sleep(random.uniform(3,8))

try:
    bot = FetchBot()
    bot.run()
except Exception as e:
    sendError('오류로 인한 종료: '+str(e))
else:
    sendError('정상적으로 종료되었습니다.')