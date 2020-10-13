import telnetlib
import json
import socket
import datetime
import re
import random

from kazoo.client import KazooClient

DEFAULT_TIMEOUT = socket._GLOBAL_DEFAULT_TIMEOUT


class Response(object):
    def __init__(self, text):
        self.text = text
        self.elapsed = None

    def json(self):
        return json.loads(self.text)


def get_address_from_zk(zk_host: str, zk_node: str):
    """从zk中获取Dubbo服务地址"""
    zk = KazooClient(hosts=zk_host)
    zk.start()
    if not zk_node.endswith('providers'):
        zk_node += '/providers'
    service_list = zk.get_children(zk_node)
    address_list = []
    for i in service_list:
        host_port = re.findall('dubbo%3A%2F%2F(.*)%3A(\d+)', i)
        address_list.extend(host_port)
    zk.stop()
    return address_list


class Dubbo(telnetlib.Telnet):
    prompt = 'dubbo>'
    coding = 'utf-8'

    def __init__(self, host=None, port=None,
                 zk_host=None, zk_node=None,
                 timeout=DEFAULT_TIMEOUT):

        if zk_host and zk_node:
            address_list = get_address_from_zk(zk_host, zk_node)
            print(address_list)
            if address_list:
                host, port = random.choice(address_list)

        super().__init__(host, port, timeout=timeout)
        self.write(b'\n')

    def command(self, flag, str_=""):
        data = self.read_until(flag.encode())
        self.write(str_.encode() + b"\n")
        return data

    def invoke(self, service_name, method_name, arg):
        command_str = "invoke {0}.{1}({2})".format(service_name, method_name, json.dumps(arg))
        self.command(Dubbo.prompt, command_str)
        start_at = datetime.datetime.now()
        data = self.command(Dubbo.prompt, "")
        data = data.decode(Dubbo.coding, errors='ignore').split('\n')[0].strip()
        # data = json.loads(data.decode(Dubbo.coding, errors='ignore').split('\n')[0].strip())
        end_at = datetime.datetime.now()
        res = Response(data)
        res.elapsed = end_at - start_at
        return res
