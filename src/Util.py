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

import os
import requests
import pickle
from bs4 import BeautifulSoup
import requests
import json
import re
from APIKey import *

DEV_MODE = False
BASE_PATH = ''


class Color:
    RED = '#de481f'
    BLUE = '#2b81c8'
    GRAY = '#aaaaaa'
    GREEN = '#00b900'


def isfile(file='data.bin', default=[]):
    if os.path.isfile(BASE_PATH+file):
        return
    else:
        save(default, file)


def save(data, file='data.bin'):
    with open(BASE_PATH+file, 'wb') as f:
        pickle.dump(data, f)


def load(file='data.bin', default=[]):
    isfile(file, default)
    with open(BASE_PATH+file, 'rb') as f:
        data = pickle.load(f)
    return data


def sendNoti(msg, img=None):
    if not DEV_MODE:
        TARGET_URL = 'https://notify-api.line.me/api/notify'
        TOKEN = API_KEY_FOR_NOTI
        response = requests.post(TARGET_URL, headers={
                                 'Authorization': 'Bearer ' + TOKEN}, data={'message': msg}, files={'imageFile': img})
        return response
    else:
        sendError(msg, img)


def sendError(msg, img=None):
    TARGET_URL = 'https://notify-api.line.me/api/notify'
    TOKEN = API_KEY_FOR_ERROR
    response = requests.post(TARGET_URL, headers={
                             'Authorization': 'Bearer ' + TOKEN}, data={'message': msg}, files={'imageFile': img})
    return response


def sendtoBot_Error(card, title='Corona Notify', notice=None):
    TOKEN = API_KEY_FOR_BOT
    if notice != None:
        with open('notice.json', 'rt', encoding='utf-8') as f:
            json_dict = json.load(f)
        json_dict['body']['contents'][0]['text'] = notice
        response = requests.post(API_REQUEST_URL, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={
                                 'to': TEST_GROUP_ID, 'messages': [{'type': 'flex', 'altText': title, 'contents': card}, {'type': 'flex', 'altText': title, 'contents': json_dict}]})
        print(response.text)
        return response
    else:
        response = requests.post(API_REQUEST_URL, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={
                                 'to': TEST_GROUP_ID, 'messages': [{'type': 'flex', 'altText': title, 'contents': card}]})
        print(response.text)
        return response


def sendtoBot_card(card, title='Corona Notify', notice=None):
    if not DEV_MODE:
        TOKEN = API_KEY_FOR_BOT
        if notice != None:
            with open('notice.json', 'rt', encoding='utf-8') as f:
                json_dict = json.load(f)
            json_dict['body']['contents'][0]['text'] = notice
            response = requests.post(API_REQUEST_URL, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={
                                     'to': GROUP_ID, 'messages': [{'type': 'flex', 'altText': title, 'contents': card}, {'type': 'flex', 'altText': title, 'contents': json_dict}]})
            print(response.text)
            return response
        else:
            response = requests.post(API_REQUEST_URL, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={
                                     'to': GROUP_ID, 'messages': [{'type': 'flex', 'altText': title, 'contents': card}]})
            print(response.text)
            return response
    else:
        sendtoBot_Error(card, title, notice)


def sendtoBot_text(text):
    if not DEV_MODE:
        tar = GROUP_ID
    else:
        tar = TEST_GROUP_ID
    TOKEN = API_KEY_FOR_BOT
    response = requests.post(API_REQUEST_URL, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={'to': tar, 'messages': [{
        "type": "text",
        "text": str(text),
    }]})
    print(response.text)
    return response


def replybyBot_card(card, replyToken, title='Corona Notify'):
    TOKEN = API_KEY_FOR_BOT
    response = requests.post('https://api.line.me/v2/bot/message/reply', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={
                             'replyToken': replyToken, 'messages': [{'type': 'flex', 'altText': title, 'contents': card}]})
    print(response.text)
    return response


def replybyBot(text, replyToken):
    TOKEN = API_KEY_FOR_BOT
    response = requests.post('https://api.line.me/v2/bot/message/reply', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={'replyToken': replyToken, 'messages': [{
        "type": "text",
        "text": str(text),
    }]})
    print(response.text)
    return response


def edit2_json(local_data, world_data, file='send2.json'):
    with open(file, 'rt', encoding='utf-8') as f:
        json_dict = json.load(f)

    base = json_dict['contents'][0]['body']['contents']
    for i in range(len(local_data)):
        if not len(local_data[i]) == 0:
            base[i]['contents'][0]['contents'][0]['text'] = local_data[i][0]  # name
            base[i]['contents'][0]['contents'][1]['text'] = local_data[i][1]  # index
            base[i]['contents'][1]['contents'][0]['contents'][0]['text'] = str(
                local_data[i][2])  # num
            base[i]['contents'][1]['contents'][0]['contents'][1]['text'] = '{:+,d}'.format(
                local_data[i][3])  # delta
            base[i]['contents'][1]['contents'][2]['contents'][0]['text'] = str(
                local_data[i][4])  # num2
            base[i]['contents'][1]['contents'][2]['contents'][1]['text'] = '{:+,d}'.format(
                local_data[i][5])  # delta

    forms = [4, 5, 5, 5, 5, 5, 5]
    cum = 0

    for c, j in enumerate(forms):
        for i in range(j):
            base = json_dict['contents'][c +
                                         1]['body']['contents'][i]['contents']

            if ((c == 0) and (i == 0)):
                for k in range(3):
                    print(world_data[cum][k])
                    base[2 *
                         k]['contents'][0]['text'] = '{:,}'.format(world_data[cum][k][0])
                    base[2*k]['contents'][1]['text'] = '{:+,d}'.format(
                        world_data[cum][k][1])
                cum += 1
                continue

            base[0]['contents'][0]['contents'][0]['text'] = '{:02}'.format(
                world_data[cum][0])
            base[0]['contents'][1]['text'] = world_data[cum][1]  # name

            delta = world_data[cum][6]
            if delta == '-':
                rank_delta = 'UN'
                rank_color = Color.GREEN
            elif delta == 0:
                rank_delta = 'NC'
                rank_color = Color.GRAY
            elif delta < 0:
                rank_delta = 'U{}'.format(delta*(-1))
                rank_color = Color.RED
            else:
                rank_delta = 'D{}'.format(delta)
                rank_color = Color.BLUE

            base[0]['contents'][0]['contents'][2]['text'] = rank_delta
            base[0]['contents'][0]['contents'][2]['color'] = rank_color

            base[1]['contents'][0]['contents'][0]['text'] = '{:,}'.format(
                world_data[cum][2])  # confirmed_num
            if world_data[cum][3] == 'NEW':
                delta = 'NEW'
            else:
                delta = '{:+,d}'.format(world_data[cum][3])
            base[1]['contents'][0]['contents'][1]['text'] = delta
            base[1]['contents'][2]['contents'][0]['text'] = '{:,}'.format(
                world_data[cum][4])  # death_num
            if world_data[cum][5] == 'NEW':
                delta = 'NEW'
            else:
                delta = '{:+,d}'.format(world_data[cum][5])
            base[1]['contents'][2]['contents'][1]['text'] = delta
            cum += 1

    return json_dict


def edit1_json(data, id, link, local_data, world_data, file='send1.json'):
    with open(file, 'rt', encoding='utf-8') as f:
        json_dict = json.load(f)

    json_dict['contents'][0]['header']['contents'][2]['text'] = '{} 기준'.format(
        data[0])

    base = json_dict['contents'][0]['body']['contents'][0]['contents']
    for i in range(3):
        j = 2*i
        base[j]['contents'][1]['contents'][0]['text'] = "{:,}".format(
            data[1][i])
        base[j]['contents'][1]['contents'][1]['text'] = "({:+,d})".format(
            data[2][i])

    json_dict['contents'][0]['body']['contents'][1]['contents'][1]['text'] = 'PIPELINE ' + \
        str(id)
    json_dict['contents'][0]['footer']['contents'][0]['action']['uri'] = link

    base = json_dict['contents'][1]['body']['contents']
    for i in range(len(local_data)):
        if not len(local_data[i]) == 0:
            base[i]['contents'][0]['contents'][0]['text'] = local_data[i][0]  # name
            base[i]['contents'][0]['contents'][1]['text'] = local_data[i][1]  # index
            base[i]['contents'][1]['contents'][0]['contents'][0]['text'] = str(
                local_data[i][2])  # num
            base[i]['contents'][1]['contents'][0]['contents'][1]['text'] = '{:+,d}'.format(
                local_data[i][3])  # delta
            base[i]['contents'][1]['contents'][2]['contents'][0]['text'] = str(
                local_data[i][4])  # num2
            base[i]['contents'][1]['contents'][2]['contents'][1]['text'] = '{:+,d}'.format(
                local_data[i][5])  # delta

    forms = [4, 5, 5, 5, 5, 5, 5]
    cum = 0

    for c, j in enumerate(forms):
        for i in range(j):
            base = json_dict['contents'][c +
                                         2]['body']['contents'][i]['contents']

            if ((c == 0) and (i == 0)):
                for k in range(3):
                    print(world_data[cum][k])
                    base[2 *
                         k]['contents'][0]['text'] = '{:,}'.format(world_data[cum][k][0])
                    base[2*k]['contents'][1]['text'] = '{:+,d}'.format(
                        world_data[cum][k][1])
                cum += 1
                continue

            base[0]['contents'][0]['contents'][0]['text'] = '{:02}'.format(
                world_data[cum][0])
            base[0]['contents'][1]['text'] = world_data[cum][1]  # name

            delta = world_data[cum][6]
            if delta == '-':
                rank_delta = 'UN'
                rank_color = Color.GREEN
            elif delta == 0:
                rank_delta = 'NC'
                rank_color = Color.GRAY
            elif delta < 0:
                rank_delta = 'U{}'.format(delta*(-1))
                rank_color = Color.RED
            else:
                rank_delta = 'D{}'.format(delta)
                rank_color = Color.BLUE

            base[0]['contents'][0]['contents'][2]['text'] = rank_delta
            base[0]['contents'][0]['contents'][2]['color'] = rank_color

            base[1]['contents'][0]['contents'][0]['text'] = '{:,}'.format(
                world_data[cum][2])  # confirmed_num
            if world_data[cum][3] == 'NEW':
                delta = 'NEW'
            else:
                delta = '{:+,d}'.format(world_data[cum][3])
            base[1]['contents'][0]['contents'][1]['text'] = delta
            base[1]['contents'][2]['contents'][0]['text'] = '{:,}'.format(
                world_data[cum][4])  # death_num
            if world_data[cum][5] == 'NEW':
                delta = 'NEW'
            else:
                delta = '{:+,d}'.format(world_data[cum][5])
            base[1]['contents'][2]['contents'][1]['text'] = delta
            cum += 1

            # with open('temp2.json', 'wt', encoding='utf-8') as f:
            #     json.dump(json_dict, f, ensure_ascii=False)

    return json_dict


def edit3_json(data, id, link, local_data, world_data, file='send3.json'):
    with open(file, 'rt', encoding='utf-8') as f:
        json_dict = json.load(f)

    json_dict['contents'][0]['body']['contents'][0]['contents'][2]['text'] = '{} 기준'.format(
        data[0])

    json_dict['contents'][0]['body']['contents'][1]['contents'][1]['text'] = 'PIPELINE ' + \
        str(id)
    json_dict['contents'][0]['footer']['contents'][0]['action']['uri'] = link

    base = json_dict['contents'][1]['body']['contents']
    for i in range(len(local_data)):
        if not len(local_data[i]) == 0:
            base[i]['contents'][0]['contents'][0]['text'] = local_data[i][0]  # name
            base[i]['contents'][0]['contents'][1]['text'] = local_data[i][1]  # index
            base[i]['contents'][1]['contents'][0]['contents'][0]['text'] = str(
                local_data[i][2])  # num
            base[i]['contents'][1]['contents'][0]['contents'][1]['text'] = '{:+,d}'.format(
                local_data[i][3])  # delta
            base[i]['contents'][1]['contents'][2]['contents'][0]['text'] = str(
                local_data[i][4])  # num2
            base[i]['contents'][1]['contents'][2]['contents'][1]['text'] = '{:+,d}'.format(
                local_data[i][5])  # delta

    forms = [4, 5, 5, 5, 5, 5, 5]
    cum = 0

    for c, j in enumerate(forms):
        for i in range(j):
            base = json_dict['contents'][c +
                                         2]['body']['contents'][i]['contents']

            if ((c == 0) and (i == 0)):
                for k in range(3):
                    print(world_data[cum][k])
                    base[2 *
                         k]['contents'][0]['text'] = '{:,}'.format(world_data[cum][k][0])
                    base[2*k]['contents'][1]['text'] = '{:+,d}'.format(
                        world_data[cum][k][1])
                cum += 1
                continue

            base[0]['contents'][0]['contents'][0]['text'] = '{:02}'.format(
                world_data[cum][0])
            base[0]['contents'][1]['text'] = world_data[cum][1]  # name

            delta = world_data[cum][6]
            if delta == '-':
                rank_delta = 'UN'
                rank_color = Color.GREEN
            elif delta == 0:
                rank_delta = 'NC'
                rank_color = Color.GRAY
            elif delta < 0:
                rank_delta = 'U{}'.format(delta*(-1))
                rank_color = Color.RED
            else:
                rank_delta = 'D{}'.format(delta)
                rank_color = Color.BLUE

            base[0]['contents'][0]['contents'][2]['text'] = rank_delta
            base[0]['contents'][0]['contents'][2]['color'] = rank_color

            base[1]['contents'][0]['contents'][0]['text'] = '{:,}'.format(
                world_data[cum][2])  # confirmed_num
            if world_data[cum][3] == 'NEW':
                delta = 'NEW'
            else:
                delta = '{:+,d}'.format(world_data[cum][3])
            base[1]['contents'][0]['contents'][1]['text'] = delta
            base[1]['contents'][2]['contents'][0]['text'] = '{:,}'.format(
                world_data[cum][4])  # death_num
            if world_data[cum][5] == 'NEW':
                delta = 'NEW'
            else:
                delta = '{:+,d}'.format(world_data[cum][5])
            base[1]['contents'][2]['contents'][1]['text'] = delta
            cum += 1

            # with open('temp2.json', 'wt', encoding='utf-8') as f:
            #     json.dump(json_dict, f, ensure_ascii=False)

    return json_dict


def table_parse(table, data):
    """
    return ['확진환자', '격리해제', '사망']
    """
    newls = []
    t = 0
    for i in range(len(table.columns)):
        tar = str(table[i][2])
        if tar.isdigit():
            if (int(tar) == data[1][t]):
                newls.append(int(table[i][3]))
                if t > 1:
                    break
                else:
                    t += 1
    if len(newls) == 3:
        return newls

    keyls = [['확진자', '확진'], ['격리해제'], ['사망']]

    newls = []
    t = 0
    for i in range(len(table.columns)):
        tar = str(table[i][1])
        if tar in keyls[t]:
            num = table[i][3].replace(',', '')
            newls.append(int(re.match('[0-9]+', num).group()))
            if t > 1:
                break
            else:
                t += 1

    return newls


class Material:
    data = []

    def __init__(self, url, id):
        self.id = id
        self.http_header1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Host': 'ncov.mohw.go.kr',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        self.url = url
        self.soup = None
        self.update = None
        self.strfupdate = None

    def request(self, url=None):
        i = 0
        if url == None:
            url = self.url
        while True:
            try:
                res = requests.get(url, headers=self.http_header1)
                res.raise_for_status()
                return res
            except Exception as e:
                i += 1
                print(e)
                if i == 5:
                    sendError('request Error: '+e)
                    raise e
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
        print('---'+self.id)
        print('PARSE: '+str(self.update))
        print('UPDATE: '+str(self.update > Material.data[0]))
        return (self.update > Material.data[0])


class Tool(Material):
    def __init__(self, url, selectors, id):
        # index 확진환자 확진환자_격리해제 사망자
        super().__init__(url, id)
        self.selectors = selectors
        self.newls = []
        self.linenum = 0
        self.test_seltem = None
        if len(Material.data) == 0:
            Material.data = load()
            if len(Material.data) == 0:
                self.set_data()
                Material.data = [self.update, self.newls[:]]
                save(Material.data)

    def test_setNextSelector(self):
        if self.test_seltem == None:
            self.test_seltem = self.selectors[0]
        self.linenum += 1
        self.selectors[0] = self.test_seltem.replace('?', str(self.linenum))
        print(self.selectors[0])

    def test_run(self):
        """
        return (self.update > Material.data[0])
        """
        res = self.request()
        self.soup = BeautifulSoup(res.text, 'html.parser')
        self.test_setNextSelector()
        try:
            self.parseUpdate()
        except TypeError:
            return False
        print('TESTRUN::P'+self.id+'::self.strfupdate '+str(self.strfupdate))
        print('TESTRUN::P'+self.id+'::self.update '+str(self.update))
        print('TESTRUN::P'+self.id+'::compare ' +
              str(self.update > Material.data[0]))
        return True

    def get_data(self):
        """
        return [self.update, self.newls, delta]
        """
        self.parseAll()
        delta = []

        if not (len(Material.data) == 0):
            for i in range(len(self.newls)):
                delta.append(self.newls[i]-Material.data[1][i])

        return [self.strfupdate, self.newls, delta]

    def set_data(self):
        res = self.request()
        self.soup = BeautifulSoup(res.text, 'html.parser')
        self.parseAll()

    def parseAll(self):
        self.newls = []

    def save_data(self):
        save([self.update, self.newls])
