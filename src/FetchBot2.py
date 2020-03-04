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

def sendNoti(msg, img=None):
    TARGET_URL = 'https://notify-api.line.me/api/notify'
    TOKEN = API_KEY_FOR_NOTI
    response = requests.post(TARGET_URL, headers={'Authorization': 'Bearer ' + TOKEN}, data={'message': msg}, files={'imageFile': img})
    return response

def sendError(msg, img=None):
    TARGET_URL = 'https://notify-api.line.me/api/notify'
    TOKEN = API_KEY_FOR_ERROR
    response = requests.post(TARGET_URL, headers={'Authorization': 'Bearer ' + TOKEN}, data={'message': msg}, files={'imageFile': img})
    return response

class Material:
    data = []
    def __init__(self, url, id):
        self.id = id
        self.http_header1 = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection':'keep-alive',
            'Host':'ncov.mohw.go.kr',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        self.url = url
        self.soup = None
        self.update = None

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

    def parseUpdate(self):
        pass

    def run(self):
        """
        return (self.update > Material.data[0])
        """
        res = self.request()
        print(res)
        self.soup = BeautifulSoup(res.text, 'html.parser')
        self.parseUpdate()
        print('PARSE: '+self.update)
        print('UPDATE: '+str(self.update > Material.data[0]))
        return (self.update > Material.data[0])

class Tool(Material):
    def __init__(self, url, selectors, id):
        # index 확진환자 확진환자_격리해제 사망자
        super().__init__(url, id)
        self.selectors = selectors
        self.newls = []
        if len(Material.data) == 0:
            Material.data = load()
            if len(Material.data) == 0:
                self.set_data()
                Material.data = [self.update, self.newls[:]]
                save(Material.data)
            
    def get_data(self):
        """
        return [self.update, self.newls, delta]
        """
        self.parseAll()
        delta = []

        if not (len(Material.data) == 0):
            for i in range(len(self.newls)):
                delta.append(self.newls[i]-Material.data[1][i])

        return [self.update, self.newls, delta]

    def set_data(self):
        res = self.request()
        self.soup = BeautifulSoup(res.text, 'html.parser')
        self.parseAll()

    def parseAll(self):
        self.newls = []

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
            print('RAW: '+self.update)
            m = re.search('\((.+)\)', self.update)
            self.update = m.group(1)
            self.update = self.update.replace('.', '월 ').replace(' 기준', '').replace('\xa0', ' ').replace('00시', '0시')
        except Exception as e:
            print("Erro u2")
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            self.update = Material.data[0]
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
            print('RAW: '+self.update)
            m = re.search('.+(\(.+\))', self.update)
            self.update = self.update.replace(m.group(1), '').replace('2020년 ', '')
        except Exception as e:
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            print("Erro u2")
            self.update = Material.data[0]
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
            print('RAW: '+self.update)
            m = re.search('\((\d+월\s*\d+일\s*\d+시)\)', self.update)
            if m:
                self.update = m.group(1)
            else:
                self.update = Material.data[0]
        except Exception as e:
            print("Error u3")
            self.update = Material.data[0]
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            # raise TypeError

class PipeLine4(Material):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun='
        super().__init__(url, '4')

    def parseUpdate(self):
        try:
            bundle = self.soup.find('div', {'class':'bvc_txt'}).findAll('p', {'class':'s_descript'})
            for idx in bundle:
                if ('총' in idx.text):
                    self.update = idx.text
                    break
            print('RAW: '+self.update)
            m = re.search('\(([0-9].+기준)\)', self.update)
            if m:
                self.update = m.group(1)
            else:
                self.update = Material.data[0]
            self.update = self.update.replace('.', '월 ').replace(' 기준','').replace('09시', '00시')
        except Exception as e:
            print("Erro u3")
            self.update = Material.data[0]
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            # raise TypeError

    def send_image(self):
        a = self.soup.find('div', {'class':'box_image'}).find('img')
        link = 'http://ncov.mohw.go.kr'+a.get('src')
        res = requests.get(link)
        sendNoti('\n전세계 코로나19 발생현황\n\nPIPELINE 4', res.content)

class PipeLine5(Tool):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun='
        super().__init__(url, None,'5')

    def parseUpdate(self):
        try:
            bundle = self.soup.find('div', {'class':'bvc_txt'}).findAll('p', {'class':'s_descript'})
            for idx in bundle:
                if ('16시' in idx.text) or ('16 시' in idx.text):
                    m = re.search('.*(\d+월)\s*(\d+일)\s*(\d+시)\s*기준', idx.text)
                    self.update = ' '.join(m.groups())
                    sendError(self.update+' 기준 데이터 발견')
                    m = re.search('\s*([0-9]+)\s*명', idx.text)
                    num = int(m.group(1))
                    self.newls.append(Material.data[1][0]+num)
                    return True
            return False
        except Exception as e:
            print("Error u5")
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            # raise TypeError
            # self.update = Material.data[0]

    def parseAll(self):
        return

    def run(self):
        res = self.request()
        print(res)
        self.soup = BeautifulSoup(res.text, 'html.parser')
        return self.parseUpdate()

    def save_data(self):
        save([self.update, [self.newls[0], Material.data[1][1], Material.data[1][2]]])
        
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
        while True:
            self.line4.run()
            print('4 업데이트 체크 중...')
            if True:
                print('4 업데이트 확인됨.')
                self.line4.send_image()
                break
            time.sleep(random.uniform(60,90))

    def run(self):
        if self.middle:
            while True:
                print('5 업데이트 체크 중...')
                if self.line5.run():
                    print('5 업데이트 확인됨.')
                    data = self.line5.get_data()
                    sendNoti("\n{} 기준 코로나 현황 업데이트\n\n확진환자수: {} ({:+d})\n\nPIPELINE 5".format(data[0], data[1][0], data[2][0]))
                    self.line5.save_data()
                    self.send_local_info()
                    return
                time.sleep(random.uniform(3,8))
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
    bot.send_img()
except Exception as e:
    sendError('오류로 인한 종료: '+str(e))
else:
    sendError('정상적으로 종료되었습니다.')