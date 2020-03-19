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
import traceback

from Util import *
from PIPELINES import PipeLine1, PipeLine2, PipeLine3, PipeLine6, PipeLine7
       
class FetchBot:
    def __init__(self, test_selector={'2':None, '3':None, '6':None}):
        if '-l' in sys.argv:
            # self.line5 = PipeLine5()
            self.middle = True
        else:
            self.middle = False
            if '--test' in sys.argv:
                self.lines = [PipeLine1(), PipeLine2(test_selector['2']), PipeLine3(test_selector['3']), PipeLine6(test_selector['6']), PipeLine7()] 
                # self.lines = [PipeLine7()]
            else:
                self.lines = [PipeLine1(), PipeLine2(), PipeLine3(), PipeLine6(), PipeLine7()]
                # self.line4 = PipeLine4()
                
    @staticmethod
    def get_local_data():
        print('Local Data 수집 시작')
        start = time.time()
        #[url, num, index]
        bundle = [['https://www.suwon.go.kr/web/safesuwon/corona/PD_index.do#none', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > table > tbody > tr > td:nth-child(1)', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > div'],
        ['http://www.yongin.go.kr/index.do', '#corona_top > div > ul > li:nth-child(1) > p', '#corona_top > div > p:nth-child(5)'],
        ['http://www.seongnam.go.kr/coronaIndex.html', '#corona_page > div.corona_page_top > div > div.contents_all > div.pc_view > table > tbody > tr > td:nth-child(1)', '#corona_page > div.corona_page_top > div > div.contents_all > span']]
        
        #[name, index, num]
        local_data = []
 
        for data in bundle:
            try:
                res = requests.get(data[0], timeout=3)
                soup = BeautifulSoup(res.text, 'html.parser')
                ni = soup.select(data[2])[0].text.split(',')
                local_data.append([ni[0], ni[1].strip(' '), soup.select(data[1])[0].text.replace('\r', '').replace('\n', '').replace('\t', '')])
            except:
                local_data.append([])
        
        try:
            res = requests.post('http://27.101.50.5/prog/stat/corona/json.do', timeout=3)
            datadict = res.json()
            index = datadict['status_date']
            m = re.search('(.+기준)', index)
            if m:
                index = m.group(1)
            local_data.append(['천안시청', index, str(datadict['item_1'])+'명'])
        except:
            local_data.append([])
        
        end = time.time()
        print('Local Data 수집 끝', end-start)
        return local_data

    @staticmethod
    def get_world_data(num):
        print('World Data 수집 시작')
        start = time.time()
        x = requests.get('https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=200&cacheHint=true')
        data_dict = x.json()

        world_data = []

        for i in range(num):
            last = int(data_dict['features'][i]['attributes']['Last_Update']/1000)
            last_str = 'KST '+time.strftime('%m.%d %H:%M', time.localtime(last))+' 기준'
            country_data = [str(i+1)+'. '+data_dict['features'][i]['attributes']['Country_Region'], last_str, data_dict['features'][i]['attributes']['Confirmed']]
            world_data.append(country_data)

        end = time.time()
        print('World Data 수집 끝', end-start)
        return world_data

    def run(self):
        if self.middle:
            sendtoBot_card(edit2_json(self.get_local_data(), self.get_world_data(10)))
        else:
            sendError('정보 수집 시작!')
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
                        sendError("PIPELINE "+line.id+'에서 업데이트 확인됨.')
                        try:
                            data = line.get_data()
                        except:
                            sendError("PIPELINE "+line.id+'에서 get_data() 오류가 발견되어 삭제합니다.')
                            self.lines.remove(line)
                            continue
                        sendtoBot_card(edit1_json(data, line.id, line.url2, self.get_local_data(), self.get_world_data(16)), 'MGLabsBot: 전일대비 {}명 증가'.format(data[2][0]))
                        line.save_data()
                        return
                    time.sleep(random.uniform(3,5))

    def test_run(self):
        if self.middle:
            sendtoBot_Error(edit2_json(self.get_local_data(), self.get_world_data(10)))
        else:
            print('테스트 정보 수집 시작!')
            while len(self.lines) != 0:
                line = self.lines[0]
                print(line.id+' 업데이트 체크 중...')
                if line.test_run():
                    print(line.id+' 업데이트 확인됨.')
                    data = line.get_data()
                    sendtoBot_Error(edit1_json(data, line.id, line.url2, self.get_local_data(), self.get_world_data(16)), 'MGLabsBot: 전일대비 {}명 증가'.format(data[2][0]))
                    self.lines.remove(line)
                time.sleep(3)
            print('테스트 완료')

    @staticmethod
    def renew(replyToken):
        data = load()
        replybyBot_card(edit1_json(data, '#RENEW', 'http://ncov.mohw.go.kr/', FetchBot.get_local_data(), FetchBot.get_world_data(16)), replyToken, 'MGLabsBot: 정보가 업데이트 되었습니다.')

try:
    if '--test' in sys.argv:
        ts = [['#listView > ul:nth-child(?) > li.title > a'], ['#content > div > div.board_list > table > tbody > tr:nth-child(?) > td.ta_l > a'], ['#sub_content > div.board_list > table > tbody > tr:nth-child(?) > td.ta_l.inl_z > a']]
        bot = FetchBot({'2':ts[0], '3':ts[1], '6':ts[2]})
        bot.test_run()
    elif '--renew' in sys.argv:
        indexnum = sys.argv.index('--renew')
        FetchBot.renew(sys.argv[indexnum+1])
    else:
        bot = FetchBot()
        bot.run()
except Exception as e:
    sendError('오류로 인한 종료: '+str(e))
    print(traceback.format_exc())
else:
    sendError('정상적으로 종료되었습니다.')