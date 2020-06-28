import requests, json
import random
import time
import threading
import string
'''
获取网址中的json数据
'''
global port
#产生数据广播出去
def Generated_data():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    sender = ''.join(random.sample(alphabet, 10))
    while True:
        amount =  random.randint(1, 10000)
        recipient = ''.join(random.sample(alphabet, 20))
        data = {
        "amount": str(amount),
        "recipient": recipient,
        "sender": sender
        }
        mine_list = requests.get('http://127.0.0.1:6000/mine_list/get')
        nodes = json.loads(mine_list.text).get("nodes")
        print("get_nodes:",nodes)
        r = requests.post(str(nodes[0]) + '/transactions/new', json=data)
        print(r)
        # 将数据发送给所有的旷工
        # nodes_count = len(nodes)
        # for i in range(nodes_count):
        #     r = requests.post(str(nodes[i-1])+'/transactions/new',json = data)
        #     print(r)
        time.sleep(2)

#获取公链中的数据
def Get_Chain():
    while True:
        time.sleep(10)
        request = requests.get('http://127.0.0.1:5000/chain')
        # request = requests.get('http://127.0.0.1:'+str(port)+'/chain' )
        state=json.loads(request.text).get("length")
        # state = json.loads(request.text).get("mine_list")
        print(state)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    threading1 = threading.Thread(target=Generated_data)
    threading2 = threading.Thread(target=Get_Chain)
    threading1.start()
    threading2.start()
    threading1.join()
    threading2.join()
    while True:
        pass

