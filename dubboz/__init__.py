import telnetlib
import json
import socket
import datetime
from urllib.parse import unquote, urlparse
import random

from kazoo.client import KazooClient

DEFAULT_TIMEOUT = socket._GLOBAL_DEFAULT_TIMEOUT


def _to_str(arg):
    if isinstance(arg, tuple):  # ensure length == 2
        type, value = arg
    else:
        type, value,  = None, arg
    if type == 'java.lang.String' or isinstance(value, str):
        return f'"{value}"'

    if isinstance(value, dict):
        if type:
            value.update({'class': type})
        return json.dumps(value)

    if isinstance(value, list):
        return json.dumps(value)  # todo

    return str(value)


class Response(object):
    def __init__(self, text, elapsed=None):
        self.text = text
        self.elapsed = elapsed

    def json(self):
        return json.loads(self.text)


class Zookeeper(KazooClient):
    def get_services(self):
        result = self.get_children(f'/dubbo')
        exclude = ('com.alibaba.dubbo.monitor.MonitorService', )
        services = [item for item in result if item not in exclude]
        return services

    def get_providers(self, service):
        """从zk中获取Dubbo服务地址"""
        result = self.get_children(f'/dubbo/{service}/providers')
        providers = [urlparse(unquote(item)).netloc.split(':') for item in result]
        return providers


class Dubbo(telnetlib.Telnet):
    prompt = 'dubbo>'
    coding = 'utf-8'

    def __init__(self, host=None, port=None, zk_hosts=None, timeout=DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.zk_hosts = zk_hosts
        self.timeout = timeout

        super().__init__(host, port, timeout=timeout)
        if self.host is not None:
            self.write(b'\n')

    def _command(self, flag, str_="") -> bytes:
        result = self.read_until(flag.encode())
        self.write(str_.encode() + b"\n")
        return result

    def command(self, cmd: str) -> str:
        self._command(Dubbo.prompt, cmd)
        result = self._command(Dubbo.prompt, "")
        result = result.decode(Dubbo.coding, errors='ignore').split('\n')[0].strip()
        return result

    def ls(self, service=None):
        cmd = "ls" if service is None else f"ls {service}"
        data = self.command(cmd)
        data = data.split('\n')
        return data

    def get_services(self):
        return self.ls()

    def get_methods(self, service):
        return self.ls(service)

    def get_providers(self, service: str):
        if self.zk_hosts is None:
            raise ValueError('No zk_hosts set')

        zk = Zookeeper(hosts=self.zk_hosts)
        zk.start()
        providers = zk.get_providers(service)
        zk.stop()
        return providers

    def invoke(self, service, method, args_str) -> str:
        cmd = f"invoke {service}.{method}({args_str})"
        result = self.command(cmd)
        print(cmd, '->', result)
        return result

    def request(self, service, method, *args)->Response:
        args_str = ','.join([_to_str(arg) for arg in args])

        if not self.host:
            providers = self.get_providers(service)
            if not providers:
                raise ValueError('Get no providers from zk')
            self.host, self.port = random.choice(providers)
            self.open(self.host, self.port, self.timeout)

        start_at = datetime.datetime.now()
        data = self.invoke(service, method, args_str)
        elapsed = datetime.datetime.now() - start_at
        res = Response(data, elapsed=elapsed)
        return res

    def request_all(self, service, method, *args)->list:
        args_str = ','.join([_to_str(arg) for arg in args])
        providers = self.get_providers(service)
        if not providers:
            raise ValueError('Get no providers from zk')
        res_list = []
        for host, port in providers:
            self.open(host, port, self.timeout)
            start_at = datetime.datetime.now()
            data = self.invoke(service, method, args_str)
            elapsed = datetime.datetime.now() - start_at
            res = Response(data, elapsed=elapsed)
            res_list.append(res)
        return res_list