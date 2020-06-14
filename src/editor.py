import pickle
import time
import sys

BASE_PATH = ''

def load(file='data.bin'):
    with open(BASE_PATH+file, 'rb') as f:
        data = pickle.load(f)
    return data

def save(data, file='data.bin'):
    with open(BASE_PATH+file, 'wb') as f:
        pickle.dump(data, f)

data = load()
if sys.argv[1].lower() == 'show':
    print(data)
    print(time.ctime(data[0]))
elif sys.argv[1].lower() == 'update':
    if sys.argv[2].lower() == 'data':
        newls = [int(i) for i in sys.argv[3:]]
        save([data[0], newls])
        print(load())
else:
    print('Command Not Found')