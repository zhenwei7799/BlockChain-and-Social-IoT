from flask import Flask, jsonify, request
import json
import requests
server = Flask(__name__)  # 创建Flask类的实例，

mine_list = []

@server.route('/mine_list/post', methods=['POST'])  # 定义URL，及访问接口的方式，URL中带有参数username
def mine_list_post():

    values = request.get_json()

    nodes = values.get('nodes')
    print(nodes)
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:

        re_data = requests.get(str(node) + '/nodes/return')
        data = json.loads(re_data.text).get("my_state")
        if data == "OK":
            mine_list.append(node)

    print(mine_list)
     # print(node)
    return jsonify("jioned"),101

@server.route('/mine_list/get', methods=['GET'])  # 定义URL，及访问接口的方式，URL中带有参数username
def mine_list_get():
    response = {
        'nodes': mine_list
    }
    print("get:",response)
    return jsonify(response), 301

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=6000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    server.run(host='127.0.0.1', port = port)
