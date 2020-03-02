import requests
from bs4 import BeautifulSoup
import re
import time
import pickle
import random
import os
import pandas as pd
from APIKey import *
import sys

# BASE_PATH = LINUX_PATH
BASE_PATH = WINDOWS_PATH

def isfile(file='data.bin'):
    if os.path.isfile(BASE_PATH+file):
        return
    else:
        save([], file)

def save(data, file='data.bin'):
    with open(BASE_PATH+file, 'wb') as f:
        pickle.dump(data, f)

def load(file='data.bin'):
    isfile(file)
    with open(BASE_PATH+file, 'rb') as f:
        data = pickle.load(f)
    return data

def sendNoti(msg):
    TARGET_URL = 'https://notify-api.line.me/api/notify'
    TOKEN = API_KEY_FOR_NOTI
    response = requests.post(TARGET_URL, headers={'Authorization': 'Bearer ' + TOKEN}, data={'message': msg})
    return response

def sendError(msg):
    TARGET_URL = 'https://notify-api.line.me/api/notify'
    TOKEN = API_KEY_FOR_ERROR
    response = requests.post(TARGET_URL, headers={'Authorization': 'Bearer ' + TOKEN}, data={'message': msg})
    return response

class Tool:
    data = []
    def __init__(self, url, selectors, id):
        self.id = id
        self.http_header1 = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection':'keep-alive',
            'Host':'ncov.mohw.go.kr',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        # index 확진환자 확진환자_격리해제 사망자
        self.url = url
        self.selectors = selectors
        self.soup = None
        self.update = None
        self.data = load()
        self.newls = []
        if len(self.data) == 0:
            self.set_data()
            self.data = [self.update, self.newls[:]]
            save(self.data)
            
    def request(self, url=None):
        if url == None:
            url = self.url
        while True:
            try:
                res = requests.get(url, headers=self.http_header1)
                res.raise_for_status()
                return res
            except:
                continue

    def get_data(self):
        """
        return [self.update, self.newls, delta]
        """
        self.parseAll()
        delta = []

        if not (len(self.data) == 0):
            for i in range(len(self.newls)):
                delta.append(self.newls[i]-self.data[1][i])

        return [self.update, self.newls, delta]

    def set_data(self):
        res = self.request()
        self.soup = BeautifulSoup(res.text, 'html.parser')
        self.parseAll()
    
    def run(self):
        """
        return (self.update > self.data[0])
        """
        res = self.request()
        print(res)
        self.soup = BeautifulSoup(res.text, 'html.parser')
        self.parseUpdate()
        print(self.update > self.data[0])
        return (self.update > self.data[0])

    def parseAll(self):
        self.newls = []
    
    def parseUpdate(self):
        pass

    def save_data(self):
        save([self.update, self.newls])

class PipeLine1(Tool):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun='
        selectors = ['#content > div > div.bv_content > div > div:nth-child(3) > table > tbody > tr:nth-child('+str(x)+') > td' for x in range(1,4)]
        selectors.insert(0, '#content > div > div.bv_content > div > p:nth-child(2)')
        super().__init__(url, selectors, '1')

    def parseAll(self):
        super().parseAll()
        try:
            if self.update == None:
                self.parseUpdate()
            for i in range(len(self.selectors)):
                if i == 0:
                    continue
                self.newls.append(int(self.soup.select(self.selectors[i])[0].text.replace('\xa0', '').replace(',','').replace('명', '')))
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            raise TypeError

    def parseUpdate(self):
        try:
            self.update = self.soup.select(self.selectors[0])[0].text #기준시간
            print(self.update)
            m = re.search('\((.+)\)', self.update)
            self.update = m.group(1)
            self.update = self.update.replace('.', '월 ').replace(' 기준', '').replace('\xa0', ' ')
        except Exception as e:
            print("Erro u2")
            print(e.with_traceback)
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            self.update = self.data[0]
            # raise TypeError

class PipeLine2(Tool):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=13&ncvContSeq=&contSeq=&board_id=&gubun='
        selectors = ['#content > div > div.data_table.tbl_scrl_mini2.mgt24 > table > tbody > tr.sumline > td:nth-child('+str(x)+')' for x in [3, 5, 6]]
        selectors.insert(0, '#content > div > div.timetable > p > span')
        super().__init__(url, selectors, '2')

    def parseAll(self):
        super().parseAll()
        try:
            if self.update == None:
                self.parseUpdate()
            for i in range(len(self.selectors)):
                if i == 0:
                    continue
                self.newls.append(int(self.soup.select(self.selectors[i])[0].text.replace(',','')))
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            raise TypeError

    def parseUpdate(self):
        try:
            self.update = self.soup.select(self.selectors[0])[0].text #기준시간
            print(self.update)
            m = re.search('.+(\(.+\))', self.update)
            self.update = self.update.replace(m.group(1), '').replace('2020년 ', '')
        except Exception as e:
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            print("Erro u2")
            print(e.with_traceback)
            self.update = self.data[0]
            # raise TypeError

class PipeLine3(Tool):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/tcmBoardList.do?brdId=&brdGubun=&dataGubun=&ncvContSeq=&contSeq=&board_id=140&gubun='
        selectors = ['#content > div > div.board_list > table > tbody > tr:nth-child(1) > td.ta_l > a']
        super().__init__(url, selectors, '3')

    def parseAll(self):
        try:
            if self.update == None:
                self.parseUpdate()
            code = self.soup.select(self.selectors[0])[0].get('onclick')
            code = code.split(',')[3].replace("'", '')
            url2 = 'http://ncov.mohw.go.kr/tcmBoardView.do?brdId=&brdGubun=&dataGubun=&ncvContSeq={0}&contSeq={0}&board_id=140&gubun=BDJ'.format(code)
            res = self.request(url2)
            ls = pd.read_html(res.text)
            table = ls[0]
            num1 = int(table[3][3])
            num2 = int(table[4][3])
            num3 = int(table[6][3])
            self.newls = [num1, num2, num3]
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            raise TypeError

    def parseUpdate(self):
        try:
            self.update = self.soup.select(self.selectors[0])[0].text #기준시간
            print(self.update)
            m = re.search('\((.+)\)', self.update)
            if m:
                self.update = m.group(1)
            else:
                self.update = self.data[0]
        except Exception as e:
            print("Erro u3")
            print(e.with_traceback)
            self.update = self.data[0]
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            # raise TypeError
        
class Factory:
    def __init__(self):
        self.line1 = PipeLine1()
        self.line2 = PipeLine2()
        self.line3 = PipeLine3()
        self.lines = [self.line1, self.line2, self.line3]

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

        sendNoti(text)

    def send_local2_info(self):
        res = requests.get('https://www.cheonan.go.kr/prog/stat/corona/json.do')
        datadict = res.json()
        num = datadict['item_1']
        index = datadict['status_date']
        text = "\n{} 천안시 코로나 현황 안내\n\n총확진자: {}".format(index, num)
        sendNoti(text)

    def run(self, argv):
        if not len(argv) == 0:
            self.send_local_info()
            self.send_local2_info()
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
                        self.send_local2_info()
                        return
                    time.sleep(random.uniform(3,8))

try:
    bot = Factory()
    bot.run(sys.argv)
except Exception as e:
    sendError('오류로 인한 종료: '+str(e))