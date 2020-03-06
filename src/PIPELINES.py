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
import re
import pandas as pd

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
            print("Erro u2 "+e)
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
            num1 = int(table.iloc[1,2])
            num2 = int(table.iloc[1,3])
            num3 = int(table.iloc[1,5])
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
            print("Error u3 "+e)
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
        a = self.soup.find('div', {'class':'box_image'}).find('img')
        link = 'http://ncov.mohw.go.kr'+a.get('src')
        res = requests.get(link)
        if res.content == self.img:
            return False
        else: 
            return True

    def send_image(self):
        del self.img
        a = self.soup.find('div', {'class':'box_image'}).find('img')
        link = 'http://ncov.mohw.go.kr'+a.get('src')
        res = requests.get(link)
        with open('world.jpg', 'wb') as f:
            f.write(res.content)
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