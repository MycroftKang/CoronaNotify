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
import time, random, sys, re, traceback

from Util import *
from LocalFetchBot import MGLocalFetchBot
from PIPELINES import PipeLine1, PipeLine2, PipeLine3, PipeLine6, PipeLine7
       
class FetchBot:
    def __init__(self, test_selector={'2':None, '3':None, '6':None}):
        if '--test' in sys.argv:
            # self.lines = [PipeLine1(), PipeLine2(test_selector['2']), PipeLine3(test_selector['3']), PipeLine6(test_selector['6']), PipeLine7()] 
            self.lines = [PipeLine1()]
        else:
            self.lines = [PipeLine1(), PipeLine2(), PipeLine3(), PipeLine6(), PipeLine7()]
            # self.line4 = PipeLine4()

    @staticmethod
    def get_world_data(num, savedata=True):
        print('World Data 수집 시작')
        start = time.time()
        x = requests.get('https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=200&cacheHint=true')
        data_dict = x.json()

        old = load('globaldata.bin', {})

        world_data = []
        default_data = ['NEW', 'NEW', '-']
        newls = {}

        for i in range(num):
            attribute = data_dict['features'][i]['attributes']
            last = int(attribute['Last_Update']/1000)
            last_str = 'KST '+time.strftime('%m.%d %H:%M', time.localtime(last))
            con_id = attribute['Country_Region']
            confirmednum = attribute['Confirmed']
            oldconfirm = old.get(con_id, default_data)[0]
            if oldconfirm == 'NEW':
                confirm_delta = 'NEW'
            else:
                confirm_delta = confirmednum-oldconfirm
            deathnum = attribute['Deaths']
            olddeath = old.get(con_id, default_data)[1]
            if olddeath == 'NEW':
                death_delta = 'NEW'
            else:
                death_delta = deathnum-olddeath
            oldrank = old.get(con_id, default_data)[2]
            if oldrank == '-':
                rank_delta = '-'
            else:
                rank_delta = (i+1)-oldrank
            country_data = [str(i+1)+'. '+con_id, last_str, confirmednum, confirm_delta, deathnum, death_delta, rank_delta]
            world_data.append(country_data)
            if savedata:
                newls[con_id]=[confirmednum, deathnum, i+1]

        if savedata:
            save(newls, 'globaldata.bin')
        
        # print(world_data)
        end = time.time()
        print('World Data 수집 끝', end-start)
        return world_data

    def run(self):
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
                    sendtoBot_card(edit1_json(data, line.id, line.url2, MGLocalFetchBot.getAll(), self.get_world_data(19)), 'MGLabsBot: 전일대비 {}명 증가'.format(data[2][0]), line.msg)
                    line.save_data()
                    return
                time.sleep(random.uniform(3,5))

    def test_run(self):
        print('테스트 정보 수집 시작!')
        while len(self.lines) != 0:
            line = self.lines[0]
            print(line.id+' 업데이트 체크 중...')
            if line.test_run():
                print(line.id+' 업데이트 확인됨.')
                data = line.get_data()
                sendtoBot_Error(edit1_json(data, line.id, line.url2, MGLocalFetchBot.getAll(False), self.get_world_data(19, False)), 'MGLabsBot: 전일대비 {}명 증가'.format(data[2][0]), line.msg)
                self.lines.remove(line)
            time.sleep(3)
        print('테스트 완료')

    @staticmethod
    def renew(replyToken):
        replybyBot_card(edit2_json(MGLocalFetchBot.getAll(False), FetchBot.get_world_data(19, False)), replyToken, 'MGLabsBot: 정보가 업데이트 되었습니다.')
        print('업데이트 완료')
        
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