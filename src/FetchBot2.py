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
import threading
import datetime

from Util import *
from LocalFetchBot import MGLocalFetchBot
from PIPELINES import PipeLine1, PipeLine2, PipeLine3, PipeLine6, PipeLine7


class FetchBot:
    def __init__(self, test_selector={'2': None, '3': None, '6': None}):
        self.global_newls = None
        if '--test' in sys.argv:
            # self.lines = [PipeLine1(), PipeLine2(test_selector['2']), PipeLine3(test_selector['3']), PipeLine6(test_selector['6']), PipeLine7()]
            self.lines = [PipeLine2(test_selector['2'])]
        else:
            self.found = False
            self.fetchdata = []
            # self.lines = [PipeLine1(), PipeLine3(), PipeLine6(), PipeLine7()]
            self.line2 = PipeLine2()
            # self.line4 = PipeLine4()

    def get_wait_time(self):
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        if (hour, minute) >= (10, 30):
            sys.exit()
        else:
            return (30, 120)

    def get_world_data(self, num, savedata=True):
        print('World Data 수집 시작')
        start = time.time()
        header = {
            'Accept': '*/*',
            'Accept-encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.arcgis.com/apps/opsdashboard/index.html',
            'Origin': 'https://www.arcgis.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
        }

        res1 = requests.get('https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Confirmed%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&cacheHint=true', headers=header)
        res2 = requests.get('https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/2/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Recovered%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&cacheHint=true', headers=header)
        res3 = requests.get('https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22Deaths%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&outSR=102100&cacheHint=true', headers=header)

        total_data = []
        for r in [res1, res2, res3]:
            data_dict = r.json()
            total_data.append(data_dict['features'][0]['attributes']['value'])

        del res1
        del res2
        del res3

        x = requests.get('https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/2/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&outSR=102100&resultOffset=0&resultRecordCount=190&cacheHint=true', headers=header)
        data_dict = x.json()

        old = load('globaldata.bin', {})

        oldtotal = old['total']
        temp = []

        for i in range(3):
            temp.append([total_data[i], total_data[i]-oldtotal[i]])

        world_data = [temp]
        default_data = ['NEW', 'NEW', '-']
        newls = {'total': total_data}

        for i in range(len(data_dict['features'])):
            if 'Korea' in data_dict['features'][i]['attributes']['Country_Region']:
                korea = i
                break

        crt = num-5

        for i in range(num):
            if i >= crt:
                i = korea + (i-crt-2)

            attribute = data_dict['features'][i]['attributes']

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
            country_data = [i+1, con_id, confirmednum,
                            confirm_delta, deathnum, death_delta, rank_delta]
            world_data.append(country_data)
            if savedata:
                newls[con_id] = [confirmednum, deathnum, i+1]

        if savedata:
            self.global_newls = newls

        # print(world_data)
        end = time.time()
        print('World Data 수집 끝', end-start)
        return world_data

    def save_global_newls(self):
        save(self.global_newls, 'globaldata.bin')

    def flow1(self):
        while not (len(self.lines) == 0):
            for line in self.lines:
                if self.found:
                    return
                if line.run():
                    if self.found:
                        return
                    self.found = True
                    try:
                        self.fetchdata = [
                            line.get_data(), line.id, line.url2, line.msg]
                    except:
                        sendError("PIPELINE "+line.id +
                                  '에서 get_data() 오류가 발견되어 삭제합니다.')
                        self.lines.remove(line)
                        continue
                    line.save_data()
                    return
                time.sleep(random.uniform(3, 5))

    def flow2(self):
        error = 0
        while not self.found:
            if self.line2.run():
                if self.found:
                    return
                self.found = True
                try:
                    self.fetchdata = [self.line2.get_data(
                    ), self.line2.id, self.line2.url2, self.line2.msg]
                except Exception as e:
                    if error < 15:
                        error += 1
                        dt = 15 * error
                        sendError("PIPELINE "+self.line2.id +
                                  '에서 get_data() "{}" 오류가 발견되어 {}초 후 다시 시작합니다.'.format(e, dt))
                        time.sleep(dt)
                        self.found = False
                        continue
                    else:
                        sendError("PIPELINE "+self.line2.id +
                                  '에서 get_data() 오류가 발견되어 삭제합니다.')
                        self.fetchdata = [[self.line2.strfupdate], self.line2.id,
                                          self.line2.url2, self.line2.msg]
                        return
                self.line2.save_data()
                return
            time.sleep(random.uniform(*self.get_wait_time()))

    def run(self):
        sendError('정보 수집 시작!')
        Ldata = MGLocalFetchBot.getAll()
        Gdata = self.get_world_data(33)
        print('Start')
        # th1 = threading.Thread(target=self.flow1)
        th2 = threading.Thread(target=self.flow2)
        # th1.start()
        th2.start()
        print('join')
        # th1.join()
        th2.join()
        print('pass')
        print(self.fetchdata)
        datals = self.fetchdata
        try:
            card = edit1_json(datals[0], datals[1], datals[2], Ldata, Gdata)
            title = 'MGYL Bot: 전일대비 {}명 증가'.format(datals[0][2][0])
        except:
            card = edit3_json(datals[0], datals[1], datals[2], Ldata, Gdata)
            title = 'MGYL Bot: {} 기준 COVID-19 현황 업데이트'.format(datals[0][0])
        sendtoBot_card(card, title, datals[3])
        self.save_global_newls()
        MGLocalFetchBot.save_newls()

    def test_run(self):
        print('테스트 정보 수집 시작!')
        while len(self.lines) != 0:
            line = self.lines[0]
            print(line.id+' 업데이트 체크 중...')
            if line.test_run():
                print(line.id+' 업데이트 확인됨.')
                data = line.get_data()
                sendtoBot_Error(edit1_json(data, line.id, line.url2, MGLocalFetchBot.getAll(
                    False), self.get_world_data(33, False)), 'MGLabsBot: 전일대비 {}명 증가'.format(data[2][0]), line.msg)
                self.lines.remove(line)
            time.sleep(3)
        print('테스트 완료')


try:
    if '--test' in sys.argv:
        ts = [['#listView > ul:nth-child(?) > li.title > a'], ['#content > div > div.board_list > table > tbody > tr:nth-child(?) > td.ta_l > a'], [
            '#sub_content > div.board_list > table > tbody > tr:nth-child(?) > td.ta_l.inl_z > a']]
        bot = FetchBot({'2': ts[0]})
        bot.test_run()
    else:
        bot = FetchBot()
        bot.run()
except Exception as e:
    sendError('오류로 인한 종료: '+str(e))
    print(traceback.format_exc())
else:
    sendError('정상적으로 종료되었습니다.')
