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


if sys.argv[1].lower() == 'show':
    data = load()
    print(data)
    print(time.ctime(data[0]))
    print(load('localdata.bin'))
elif sys.argv[1].lower() == 'update':
    if sys.argv[2].lower() == 'global':
        data = load()
        newls = [int(i) for i in sys.argv[3:]]
        save([data[0], newls])
        print(load())
    elif sys.argv[2].lower() == 'local':
        if sys.argv[3].lower() == 'setup':
            data = load('localdata.bin')
            for i, v in enumerate(data):
                data[i] = [v, 0]
            save(data, 'localdata.bin')
            print(load('localdata.bin'))
        else:
            data = load('localdata.bin')
            newls = [int(i) for i in sys.argv[3:]]
            data[newls[0]] = [newls[1], newls[2]]
            save(data, 'localdata.bin')
            print(load('localdata.bin'))
else:
    print('Command Not Found')
