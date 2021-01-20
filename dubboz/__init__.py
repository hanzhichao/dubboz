import telnetlib
import json
import re
import socket
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
    """Dubbo Client"""
    prompt = 'dubbo>'
    coding = 'utf-8'

    def __init__(self, host=None, port=None, timeout=DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
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
        result = result.decode(Dubbo.coding, errors='ignore').rstrip(self.prompt).strip()
        return result

    def ls(self, service=None):
        cmd = "ls" if service is None else f"ls {service}"
        cmd_result = self.command(cmd)
        data = [item.strip() for item in cmd_result.split('\n') if item.strip()]
        return data

    def get_services(self):
        return self.ls()

    def get_methods(self, service):
        return self.ls(service)

    def invoke(self, service, method, *args) -> str:
        args_str = ','.join([_to_str(arg) for arg in args])
        cmd = f"invoke {service}.{method}({args_str})"
        cmd_result = self.command(cmd)
        data = [item.strip() for item in cmd_result.split('\n') if item.strip()]
        if len(data) < 2:
            raise ValueError('无该方法，方法或参数签名不正确')
        result, elapsed_line = cmd_result.split('\n')
        elapsed = int(re.search(r'\d+', elapsed_line).group())
        result = result.strip().strip('"')
        return result, elapsed


class Service(object):
    def __init__(self, registry: str, name: str):
        """
        Dubbo Service
        :param registry: dubbo://127.0.0.1:20880 or zookeeper://192.168.1.9:2181
        :param name: Service name
        """
        self.name = name
        self.registry = registry
        self.provider = None
        self.providers = []
        self.zk_cli = None  # zk client
        self.dubbo_cli = None
        self.methods = []

        self._get_provider()
        self._get_methods()

    def _get_provider(self):
        # 1. 获取registry类型
        self.registry_type = self.registry.split('://')[0] if isinstance(self.registry, str) else None
        # 2. 获取provider和providers
        if self.registry_type == 'dubbo':
            self.provider = self.registry
            self.providers = [self.provider]
        elif self.registry_type == 'zookeeper':
            self.zk_cli = Zookeeper(hosts=self.registry)
            self.providers = self.zk_cli.get_providers(self.name)
            self.provider = random.choice(self.providers)
        else:
            raise NotImplemented('目前仅支持dubbo和zookeeper')

    def _get_methods(self):
        self.dubbo_cli = self._get_dubbo_cli(self.provider)
        if self.dubbo_cli is None:
            raise ValueError('未提供provider')
        self.methods = self.dubbo_cli.get_methods(self.name)

    @staticmethod
    def _get_dubbo_cli(provider):
        host, port = provider.lstrip('dubbo://').split(':')
        dubbo_cli = Dubbo(host=host, port=port)
        return dubbo_cli

    def call(self, method, *args, index=None):
        if index is None:
            dubbo_cli = self.dubbo_cli
        else:
            provider = self.providers[index]
            dubbo_cli = self._get_dubbo_cli(provider)
        return dubbo_cli.invoke(self.name, method, *args)

    def call_all(self, method, *args):
        results = [self.call(method, *args, index=index) for index, _ in enumerate(self.providers)]
        return results

    def __getattr__(self, item):
        return lambda *args: self.call(item, *args)[0]



import telnetlib
import json
import re
import socket
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


class Zookeeper(KazooClient):
    def get_services(self):
        result = self.get_children(f'/dubbo')
        exclude = ('com.alibaba.dubbo.monitor.MonitorService', )
        services = [item for item in result if item not in exclude]
        return services

    def get_providers(self, service):
        """从zk中获取Dubbo服务地址"""
        result = self.get_children(f'/dubbo/{service}/providers')
        providers = [urlparse(unquote(item)).netloc for item in result]
        return providers


class Dubbo(telnetlib.Telnet):
    """Dubbo Client"""
    prompt = 'dubbo>'
    coding = 'utf-8'

    def __init__(self, host=None, port=None, timeout=DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
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
        result = result.decode(Dubbo.coding, errors='ignore').rstrip(self.prompt).strip()
        return result

    def ls(self, service=None):
        cmd = "ls" if service is None else f"ls {service}"
        cmd_result = self.command(cmd)
        data = [item.strip() for item in cmd_result.split('\n') if item.strip()]
        return data

    def get_services(self):
        return self.ls()

    def get_methods(self, service):
        return self.ls(service)

    def invoke(self, service, method, *args) -> str:
        args_str = ','.join([_to_str(arg) for arg in args])
        cmd = f"invoke {service}.{method}({args_str})"
        cmd_result = self.command(cmd)
        data = [item.strip() for item in cmd_result.split('\n') if item.strip()]
        if len(data) < 2:
            raise ValueError('无该方法，方法或参数签名不正确')
        result, elapsed_line = cmd_result.split('\n')
        elapsed = int(re.search(r'\d+', elapsed_line).group())
        result = result.strip().strip('"')
        return result, elapsed


class Service(object):
    def __init__(self, registry: str, name: str):
        """
        Dubbo Service
        :param registry: dubbo://127.0.0.1:20880 or zookeeper://192.168.1.9:2181
        :param name: Service name
        """
        self.name = name
        self.registry = registry
        self.provider = None
        self.providers = []
        self.zk_cli = None  # zk client
        self.dubbo_cli = None
        self.methods = []

        self._get_provider()
        self._get_methods()

    def _get_provider(self):
        # 1. 获取registry类型
        self.registry_type = self.registry.split('://')[0] if isinstance(self.registry, str) else None
        # 2. 获取provider和providers
        if self.registry_type == 'dubbo':
            self.provider = self.registry
            self.providers = [self.provider]
        else:
            self.zk_cli = Zookeeper(hosts=self.registry)
            self.zk_cli.start()
            self.providers = self.zk_cli.get_providers(self.name)
            self.zk_cli.stop()
            self.provider = random.choice(self.providers)

    def _get_methods(self):
        self.dubbo_cli = self._get_dubbo_cli(self.provider)  #
        if self.dubbo_cli is None:
            raise ValueError('未提供provider')
        self.methods = self.dubbo_cli.get_methods(self.name)

    @staticmethod
    def _get_dubbo_cli(provider):
        host, port = provider.lstrip('dubbo://').split(':')  # AttributeError: 'list' object has no attribute 'lstrip'
        dubbo_cli = Dubbo(host=host, port=port)
        return dubbo_cli

    def call(self, method, *args, index=None):
        if index is None:
            dubbo_cli = self.dubbo_cli
        else:
            provider = self.providers[index]
            dubbo_cli = self._get_dubbo_cli(provider)
        return dubbo_cli.invoke(self.name, method, *args)

    def call_all(self, method, *args):
        results = [self.call(method, *args, index=index) for index, _ in enumerate(self.providers)]
        return results

    def __getattr__(self, item):
        return lambda *args: self.call(item, *args)[0]

