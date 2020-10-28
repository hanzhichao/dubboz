from flask import Flask, request, jsonify, abort, Response

from dubboz import Dubbo

app = Flask(__name__)


@app.route('/dubbo', methods=['GET', 'POST'])
def dubbo():
    values = request.json
    if not values:
        return abort(Response('参数应为JSON格式', 400))
    host = values.get('host') or request.values.get('host')
    port = values.get('port') or request.values.get('port')
    zk_hosts = values.get('zk_hosts') or request.values.get('zk_hosts')

    service = values.get('service')
    method = values.get('method')
    args = values.get('args', [])

    cli = Dubbo(host=host, port=port, zk_hosts=zk_hosts)
    res = cli.request(service, method, *args)
    try:
        return jsonify(res.json())
    except:
        return res.text


if __name__ == '__main__':
    app.run()


