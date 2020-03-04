import os
import requests
import pickle
from bs4 import BeautifulSoup
import requests
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