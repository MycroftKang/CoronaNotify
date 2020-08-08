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

from Util import *
import time
import re
import pandas as pd
import datetime

# Cov19 발생동향


class PipeLine1(Tool):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun='
        selectors = [
            '#content > div > div:nth-child(5) > table > tbody > tr > td:nth-child('+str(x)+')' for x in [1, 2, 4]]
        self.msg = None
        selectors.insert(0, '#content > div > p')
        super().__init__(url, selectors, '1')

    def parseAll(self):
        super().parseAll()
        try:
            if self.update == None:
                self.parseUpdate()
            for i in range(len(self.selectors)):
                if i == 0:
                    continue
                self.newls.append(int(self.soup.select(self.selectors[i])[
                                  0].text.replace('\xa0', '').replace(',', '').replace('명', '')))
            self.url2 = self.url
            print('NEWLS', self.newls)
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            raise TypeError

    def parseUpdate(self):
        try:
            updatestr = self.soup.select(self.selectors[0])[0].text  # 기준시간
            print('RAW: '+updatestr)
            m = re.search('\((\d+)\D+(\d+)\D+(\d+시).*\)', updatestr)
            updatestr = '{}월 {}일 {}'.format(m.group(1), m.group(2), m.group(3))
            updatestr = updatestr.replace('00시', '0시')
            self.strfupdate = updatestr
            self.update = time.mktime(time.strptime(
                '2020년 '+updatestr, '%Y년 %m월 %d일 %H시'))
        except Exception as e:
            print("Erro u2 "+str(e))
            # raise e
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            self.update = Material.data[0]
            # raise TypeError

# 질병관리본부


class PipeLine2(Tool):
    def __init__(self, test_selectors=None):
        url = 'https://www.cdc.go.kr/board/board.es?mid=a20501000000&bid=0015'
        if test_selectors == None:
            selectors = ['#listView > ul:nth-child(1) > li.title > a']
            self.TEST_MODE = False
        else:
            selectors = test_selectors
            self.TEST_MODE = True
        super().__init__(url, selectors, '2')
        self.msg = '이 파이프라인은 Learn more을 통해\n지역별 상세 통계를 제공합니다.'
        self.http_header1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'www.cdc.go.kr',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    def parseAll(self):
        try:
            if self.update == None:
                self.parseUpdate()
            link = self.soup.select(self.selectors[0])[0].get('href')
            self.url2 = 'https://www.cdc.go.kr'+link
            res = self.request(self.url2)
            ls = pd.read_html(res.text)
            print(ls[0])
            print(ls[1])
            print(ls[2])
            try:
                self.newls = table_parse2(ls[0], ls[1], ls[2])
            except:
                try:
                    self.newls = table_parse(ls[0], self.data)
                except:
                    self.newls = []
                    raise TypeError
            print('NEWLS', self.newls)
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            print(res.text)
            raise e

    def parseUpdate(self):
        try:
            updatestr = self.soup.select(self.selectors[0])[
                0].get('title')  # 기준시간
            print('RAW: '+updatestr)
            m = re.search(
                '\(((?P<month>\d+)월\s*(?P<date>\d+)일.*?(?P<hour>\d+)시.*?)\)', updatestr)
            if m:
                timedict: dict = m.groupdict()
                timedict = dict([k, int(v)] for k, v in timedict.items())
                d = datetime.datetime(
                    2020, timedict['month'], timedict['date'], timedict['hour'], 0, 0)
                self.strfupdate = f"{timedict['month']}월 {timedict['date']}일 {timedict['hour']}시"
                self.update = d.timestamp()
            elif self.TEST_MODE:
                raise TypeError
            else:
                self.update = Material.data[0]
        except TypeError as e:
            raise e
        except Exception as e:
            print("Error u3 "+str(e))
            self.update = Material.data[0]
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            # raise TypeError

    def test_setNextSelector(self):
        if self.test_seltem == None:
            self.test_seltem = self.selectors[0]
        self.linenum += 1
        self.selectors[0] = self.test_seltem.replace(
            '?', str(2*self.linenum-1))

# Cov19


class PipeLine3(Tool):
    def __init__(self, test_selectors=None):
        url = 'http://ncov.mohw.go.kr/tcmBoardList.do?brdId=&brdGubun=&dataGubun=&ncvContSeq=&contSeq=&board_id=140&gubun='
        if test_selectors == None:
            selectors = [
                '#content > div > div.board_list > table > tbody > tr:nth-child(1) > td.ta_l > a']
            self.TEST_MODE = False
        else:
            selectors = test_selectors
            self.TEST_MODE = True
        super().__init__(url, selectors, '3')
        self.msg = '이 파이프라인은 Learn more을 통해\n지역별 상세 통계를 제공합니다.'

    def parseAll(self):
        try:
            if self.update == None:
                self.parseUpdate()
            code = self.soup.select(self.selectors[0])[0].get('onclick')
            code = code.split(',')[3].replace("'", '')
            self.url2 = 'http://ncov.mohw.go.kr/tcmBoardView.do?brdId=&brdGubun=&dataGubun=&ncvContSeq={0}&contSeq={0}&board_id=140&gubun=BDJ'.format(
                code)
            res = self.request(self.url2)
            ls = pd.read_html(res.text)
            table = ls[0]
            try:
                self.newls = table_parse(table, self.data)
            except:
                num1 = int(table.iloc[1, 2])
                num2 = int(table.iloc[1, 3])
                num3 = int(table.iloc[1, 5])
                self.newls = [num1, num2, num3]
            print('NEWLS', self.newls)
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            raise TypeError

    def parseUpdate(self):
        try:
            updatestr = self.soup.select(self.selectors[0])[0].text  # 기준시간
            print('RAW: '+updatestr)
            m = re.search('\((\d+월\s*\d+일.*\d+시.*)\)', updatestr)
            if m:
                updatestr = m.group(1).strip()
                self.strfupdate = updatestr
                self.update = time.mktime(time.strptime(
                    '2020년 '+updatestr, '%Y년 %m월 %d일 %H시'))
            elif self.TEST_MODE:
                raise TypeError('매칭되지 않음')
            else:
                self.update = Material.data[0]
        except TypeError as e:
            raise e
        except Exception as e:
            print("Error u3 "+str(e))
            self.update = Material.data[0]
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            # raise TypeError


class PipeLine4(Material):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun='
        super().__init__(url, '4')

    def load_img(self):
        with open('world.jpg', 'rb') as f:
            self.img = f.read()

    def run(self):
        """
        return (self.update > Material.data[0])
        """
        res = self.request()
        print(res)
        self.soup = BeautifulSoup(res.text, 'html.parser')
        return self.Check_Update()

    def Check_Update(self):
        a = self.soup.find('div', {'class': 'box_image'}).find('img')
        link = 'http://ncov.mohw.go.kr'+a.get('src')
        res = requests.get(link)
        if res.content == self.img:
            return False
        else:
            return True

    def send_image(self):
        del self.img
        a = self.soup.find('div', {'class': 'box_image'}).find('img')
        link = 'http://ncov.mohw.go.kr'+a.get('src')
        res = requests.get(link)
        with open('world.jpg', 'wb') as f:
            f.write(res.content)
        sendNoti('\n전세계 코로나19 발생현황\n\nPIPELINE 4', res.content)


class PipeLine5(Tool):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun='
        super().__init__(url, None, '5')

    def parseUpdate(self):
        try:
            bundle = self.soup.find('div', {'class': 'bvc_txt'}).findAll(
                'p', {'class': 's_descript'})
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
            print("Error u5 "+e)
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))

    def parseAll(self):
        return

    def run(self):
        res = self.request()
        print(res)
        self.soup = BeautifulSoup(res.text, 'html.parser')
        return self.parseUpdate()

    def save_data(self):
        save([self.update, [self.newls[0], Material.data[1][1], Material.data[1][2]]])

# 보건복지부


class PipeLine6(Tool):
    def __init__(self, test_selectors=None):
        url = 'http://www.mohw.go.kr/react/al/sal0301ls.jsp?PAR_MENU_ID=04&MENU_ID=0403'
        if test_selectors == None:
            selectors = [
                '#sub_content > div.board_list > table > tbody > tr:nth-child(1) > td.ta_l.inl_z > a']
            self.TEST_MODE = False
        else:
            selectors = test_selectors
            self.TEST_MODE = True
        super().__init__(url, selectors, '6')
        self.msg = '이 파이프라인은 Learn more을 통해\n지역별 상세 통계를 제공합니다.'
        self.http_header1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'www.mohw.go.kr',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    def parseAll(self):
        try:
            if self.update == None:
                self.parseUpdate()
            link = self.soup.select(self.selectors[0])[0].get('href')
            self.url2 = 'http://www.mohw.go.kr'+link
            res = self.request(self.url2)
            ls = pd.read_html(res.text)
            table = ls[0]
            try:
                self.newls = table_parse(table, self.data)
            except:
                num1 = int(table.iloc[1, 2])
                num2 = int(table.iloc[1, 3])
                num3 = int(table.iloc[1, 5])
                self.newls = [num1, num2, num3]
            print('NEWLS', self.newls)
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            raise TypeError

    def parseUpdate(self):
        try:
            updatestr = self.soup.select(self.selectors[0])[0].text  # 기준시간
            print('RAW: '+updatestr)
            m = re.search('\((\d+월\s*\d+일.*\d+시.*)\)', updatestr)
            if m:
                updatestr = m.group(1).strip()
                self.strfupdate = updatestr
                self.update = time.mktime(time.strptime(
                    '2020년 '+updatestr, '%Y년 %m월 %d일 %H시'))
            elif self.TEST_MODE:
                raise TypeError
            else:
                self.update = Material.data[0]
        except TypeError as e:
            raise e
        except Exception as e:
            print("Error u3 "+str(e))
            self.update = Material.data[0]
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            # raise TypeError


class PipeLine7(Tool):
    def __init__(self):
        url = 'http://ncov.mohw.go.kr/'
        selectors = ['body > div > div.mainlive_container > div > div > div > div.live_left > div.liveNum > ul > li:nth-child('+str(
            x)+') > span.num' for x in [1, 2, 4]]
        selectors.insert(
            0, 'body > div > div.mainlive_container > div > div > div > div.live_left > h2 > a > span')
        super().__init__(url, selectors, '7')
        self.msg = None

    def parseAll(self):
        super().parseAll()
        try:
            if self.update == None:
                self.parseUpdate()
            for i in range(len(self.selectors)):
                if i == 0:
                    continue
                self.newls.append(int(self.soup.select(self.selectors[i])[0].text.replace(
                    '\xa0', '').replace(',', '').replace('명', '').replace('(누적)', '')))
            self.url2 = self.url
            print('NEWLS', self.newls)
        except Exception as e:
            sendError(self.id+' parseAll 오류가 발생했습니다. '+str(e))
            raise TypeError

    def parseUpdate(self):
        try:
            updatestr = self.soup.select(self.selectors[0])[0].text  # 기준시간
            print('RAW: '+updatestr)
            m = re.search('\((\d+)\D+(\d+)\D+(\d+시).*\)', updatestr)
            updatestr = '{}월 {}일 {}'.format(m.group(1), m.group(2), m.group(3))
            updatestr = updatestr.replace('00시', '0시')
            self.strfupdate = updatestr
            self.update = time.mktime(time.strptime(
                '2020년 '+updatestr, '%Y년 %m월 %d일 %H시'))
        except Exception as e:
            print("Erro u7 "+str(e))
            # raise e
            # sendError(self.id+' parseUpdate 오류가 발생했습니다. '+str(e))
            self.update = Material.data[0]
            # raise TypeError
