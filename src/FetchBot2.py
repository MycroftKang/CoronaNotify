import requests
from bs4 import BeautifulSoup
import time
import random
import sys

from Util import *
from PIPELINES import PipeLine1, PipeLine3, PipeLine4, PipeLine5
       
class FetchBot:
    def __init__(self):
        if not len(sys.argv) == 1:
            self.line5 = PipeLine5()
            self.middle = True
        else:
            self.lines = [PipeLine1(), PipeLine3()]
            self.line4 = PipeLine4()
            self.middle = False

    def send_local_info(self):
        #[url, num, index]
        bundle = [['https://www.suwon.go.kr/web/safesuwon/corona/PD_index.do#none', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > table > tbody > tr > td:nth-child(2) > a', 'body > div.layout > div > ul > li:nth-child(1) > div > div.status.clearfix > div'],
        ['http://www.yongin.go.kr/health/ictsd/index.do', '#coronabox_1 > div.coronacon_le > div > div:nth-child(1) > div > table > tbody > tr:nth-child(1) > td > b', '#coronabox_1 > div.coronacon_le > div > div:nth-child(1) > h4 > span']]
        num = []
        index = []

        for data in bundle:
            res = requests.get(data[0])
            soup = BeautifulSoup(res.text, 'html.parser')
            num.append(soup.select(data[1])[0].text)
            index.append(soup.select(data[2])[0].text.replace(', ', ':\n'))

        text = '\n지역별 코로나 현황 안내'

        for i in range(len(num)):
            text = text + '\n\n'+index[i] + ' ' + num[i]

        text = text + self.get_local2_info()

        sendNoti(text)

    def get_local2_info(self):
        res = requests.post('http://27.101.50.5/prog/stat/corona/json.do')
        datadict = res.json()
        num = datadict['item_1']
        index = datadict['status_date']
        text = "\n\n천안시청:\n{} {}명".format(index, num)
        return text

    def send_img(self):
        self.line4.load_img()
        while True:
            print('4 업데이트 체크 중...')
            if self.line4.run():
                print('4 업데이트 확인됨.')
                self.line4.send_image()
                break
            time.sleep(random.uniform(60,90))

    def run(self):
        if self.middle:
            self.send_local_info()
            # while True:
            #     print('5 업데이트 체크 중...')
            #     if self.line5.run():
            #         print('5 업데이트 확인됨.')
            #         # data = self.line5.get_data()
            #         # sendNoti("\n{} 기준 코로나 현황 업데이트\n\n확진환자수: {} ({:+d})\n\nPIPELINE 5".format(data[0], data[1][0], data[2][0]))
            #         # self.line5.save_data()
            #         self.send_local_info()
            #         return
            #     time.sleep(random.uniform(7,15))
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
                        numls = data[1]
                        delta = data[2]
                        sendNoti("\n{} 기준 코로나 현황 업데이트\n\n확진환자수: {} ({:+d})\n확진환자 격리해제수: {} ({:+d})\n사망자수: {} ({:+d})\n\nPIPELINE {}".format(data[0], numls[0], delta[0], numls[1], delta[1], numls[2], delta[2], line.id))
                        line.save_data()
                        self.send_local_info()
                        self.send_img()
                        return
                    time.sleep(random.uniform(3,8))

try:
    bot = FetchBot()
    bot.run()
except Exception as e:
    sendError('오류로 인한 종료: '+str(e))
else:
    sendError('정상적으로 종료되었습니다.')