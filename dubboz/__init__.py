import telnetlib
import json
import socket
import datetime


class Dubbo(telnetlib.Telnet):
    prompt = 'dubbo>'
    coding = 'utf-8'

    def __init__(self, host=None, port=0, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        super().__init__(host, port)
        self.write(b'\n')

    def command(self, flag, str_=""):
        data = self.read_until(flag.encode())
        self.write(str_.encode() + b"\n")
        return data

    def invoke(self, service_name, method_name, arg):
        command_str = "invoke {0}.{1}({2})".format(service_name, method_name, json.dumps(arg))
        self.command(Dubbo.prompt, command_str)
        s = datetime.datetime.now()
        data = self.command(Dubbo.prompt, "")
        data = data.decode(Dubbo.coding, errors='ignore').split('\n')[0].strip()
        # data = json.loads(data.decode(Dubbo.coding, errors='ignore').split('\n')[0].strip())
        e = datetime.datetime.now()
        print(e - s)
        return data
