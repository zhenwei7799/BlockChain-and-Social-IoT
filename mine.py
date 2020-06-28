from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
import requests, json
import time
import threading
# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

#旷工
@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 给工作量证明的节点提供奖励.
    # 发送者为 "0" 表明是新挖出的币
    # blockchain.new_transaction(
    #     sender="0",
    #     recipient=node_identifier,
    #     amount=1,
    # )

    # Forge the new Block by adding it to the chain
    block = blockchain.new_block(proof, None)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'hash':blockchain.hash(block),
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

#增加交易
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # 检查POST数据
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

#当前链的信息
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
        "mine_list": list(blockchain.nodes),
    }
    return jsonify(response), 200

#增加节点
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    print(nodes)
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

'''
取代上一个链
'''
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/pending_tx', methods=['GET'])
def get_pending_tx():
    data =  blockchain.current_transactions
    print(data)
    if len(data) == 0:
        return "There is no current transaction ", 400
    else:
        return jsonify(data), 300

global port
'''
回复本身储存的节点数
'''
@app.route('/nodes/list', methods=['GET'])
def list_nodes():
    response = {
        'nodes': list(blockchain.nodes)
    }
    return jsonify(response), 200

'''
确认在线
'''
@app.route('/nodes/return', methods=['GET'])
def return_nodes():
    response = {
        'my_state': "OK"
    }
    return jsonify(response), 301

def mine_thread():
    time.sleep(1)
    #将自身的IP和端口加入网络
    a = {"nodes": ['http://127.0.0.1:'+str(port)]}
    requests.post('http://127.0.0.1:6000/mine_list/post', json = a)

    while True:
        #查询有无交易未被处理
        data = blockchain.current_transactions
        if len(data) != 0:
            #如果存在没有处理的交易，进行mine
            request = requests.get('http://127.0.0.1:'+str(port)+'/mine?projectId=%s')
            result = json.loads(request.text).get('message')
            print(result)
        else:
            print("There is no current transaction")
        time.sleep(5)

if __name__ == '__main__':
#def run(Host,Port):
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    mine_threading = threading.Thread(target=mine_thread)
    mine_threading.start()

    app.run(host='127.0.0.1', port = port)
    #开线程，每个一段时间检查有无未挖矿的数据
    mine_threading.join()

