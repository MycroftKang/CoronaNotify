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
from APIKey import *

DEV_MODE = False
BASE_PATH=''

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
    if not DEV_MODE:
        TARGET_URL = 'https://notify-api.line.me/api/notify'
        TOKEN = API_KEY_FOR_NOTI
        response = requests.post(TARGET_URL, headers={'Authorization': 'Bearer ' + TOKEN}, data={'message': msg}, files={'imageFile': img})
        return response
    else:
        sendError(msg, img)

def sendError(msg, img=None):
    TARGET_URL = 'https://notify-api.line.me/api/notify'
    TOKEN = API_KEY_FOR_ERROR
    response = requests.post(TARGET_URL, headers={'Authorization': 'Bearer ' + TOKEN}, data={'message': msg}, files={'imageFile': img})
    return response

def sendtoBot_Error(card):
    TOKEN = API_KEY_FOR_BOT
    response = requests.post(API_REQUEST_URL, headers={'Content-Type':'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={'to':TEST_GROUP_ID,'messages':[{'type':'flex', 'altText':'Corona Notify', 'contents':card}]})
    print(response.text)
    return response

def sendtoBot_card(card):
    if not DEV_MODE:
        TOKEN = API_KEY_FOR_BOT
        response = requests.post(API_REQUEST_URL, headers={'Content-Type':'application/json', 'Authorization': 'Bearer ' + TOKEN}, json={'to':GROUP_ID,'messages':[{'type':'flex', 'altText':'Corona Notify', 'contents':card}]})
        print(response.text)
        return response
    else:
        sendtoBot_Error(card)

def edit2_json(local_data, file='send2.json'):
    with open(file, 'rt', encoding='utf-8') as f:
        json_dict = json.load(f)
    
    if not len(local_data[0]) == 0:
        json_dict['body']['contents'][3]['contents'][0]['text'] = local_data[0][0] #name
        json_dict['body']['contents'][3]['contents'][1]['contents'][0]['text'] = local_data[0][1] #index
        json_dict['body']['contents'][3]['contents'][1]['contents'][1]['text'] = local_data[0][2] #num

    if not len(local_data[1]) == 0:
        json_dict['body']['contents'][4]['contents'][0]['text'] = local_data[1][0] #name
        json_dict['body']['contents'][4]['contents'][1]['contents'][0]['text'] = local_data[1][1] #index
        json_dict['body']['contents'][4]['contents'][1]['contents'][1]['text'] = local_data[1][2] #num

    if not len(local_data[2]) == 0:
        json_dict['body']['contents'][5]['contents'][0]['text'] = local_data[2][0] #name
        json_dict['body']['contents'][5]['contents'][1]['contents'][0]['text'] = local_data[2][1] #index
        json_dict['body']['contents'][5]['contents'][1]['contents'][1]['text'] = '{}명'.format(local_data[2][2]) #num

    if not len(local_data[3]) == 0:
        json_dict['body']['contents'][6]['contents'][0]['text'] = local_data[3][0] #name
        json_dict['body']['contents'][6]['contents'][1]['contents'][0]['text'] = local_data[3][1] #index
        json_dict['body']['contents'][6]['contents'][1]['contents'][1]['text'] = '{}명'.format(local_data[3][2]) #num

    return json_dict

def edit1_json(data, id, local_data, file='send1.json'):
    with open(file, 'rt', encoding='utf-8') as f:
        json_dict = json.load(f)
    
    json_dict['contents'][0]['body']['contents'][2]['text'] = '{} 기준'.format(data[0])
    json_dict['contents'][0]['body']['contents'][4]['contents'][0]['contents'][1]['text'] = "{} ({:+d})".format(data[1][0], data[2][0])
    json_dict['contents'][0]['body']['contents'][4]['contents'][1]['contents'][1]['text'] = "{} ({:+d})".format(data[1][1], data[2][1])
    json_dict['contents'][0]['body']['contents'][4]['contents'][2]['contents'][1]['text'] = "{} ({:+d})".format(data[1][2], data[2][2])
    json_dict['contents'][0]['body']['contents'][6]['contents'][0]['text'] = 'PIPELINE '+str(id)

    if not len(local_data[0]) == 0:
        json_dict['contents'][1]['body']['contents'][2]['contents'][0]['text'] = local_data[0][0] #name
        json_dict['contents'][1]['body']['contents'][2]['contents'][1]['contents'][0]['text'] = local_data[0][1] #index
        json_dict['contents'][1]['body']['contents'][2]['contents'][1]['contents'][1]['text'] = local_data[0][2] #num
    
    if not len(local_data[1]) == 0:
        json_dict['contents'][1]['body']['contents'][3]['contents'][0]['text'] = local_data[1][0] #name
        json_dict['contents'][1]['body']['contents'][3]['contents'][1]['contents'][0]['text'] = local_data[1][1] #index
        json_dict['contents'][1]['body']['contents'][3]['contents'][1]['contents'][1]['text'] = local_data[1][2] #num
    
    if not len(local_data[2]) == 0:
        json_dict['contents'][1]['body']['contents'][4]['contents'][0]['text'] = local_data[2][0] #name
        json_dict['contents'][1]['body']['contents'][4]['contents'][1]['contents'][0]['text'] = local_data[2][1] #index
        json_dict['contents'][1]['body']['contents'][4]['contents'][1]['contents'][1]['text'] = '{}명'.format(local_data[2][2]) #num
    
    if not len(local_data[3]) == 0:
        json_dict['contents'][1]['body']['contents'][5]['contents'][0]['text'] = local_data[3][0] #name
        json_dict['contents'][1]['body']['contents'][5]['contents'][1]['contents'][0]['text'] = local_data[3][1] #index
        json_dict['contents'][1]['body']['contents'][5]['contents'][1]['contents'][1]['text'] = '{}명'.format(local_data[3][2]) #num

    return json_dict
     
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
        i = 0
        if url == None:
            url = self.url
        while True:
            try:
                res = requests.get(url, headers=self.http_header1)
                res.raise_for_status()
                return res
            except Exception as e:
                i+=1
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