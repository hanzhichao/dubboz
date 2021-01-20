# Dubboz
简单易用的Dubbo客户端

## 特性
* 支持Dubbo直连和使用Zookeeper
* 支持获取providers
* 支持使用call all providers
## 安装方法
```.sh
pip install dubboz
```

## 使用方法
### 使用Zookeeper
```python
import json
from dubboz import Service

service = Service(
    registy='127.0.0.1:5181?backup=127.0.0.1:5182,127.0.0.1:5183',
    name='com.***.rpc.order.OrderService')  # 连接zk获取服务
print(service.providers)
print(service.provider)
print(service.methods)
result = service.queryOrderDateByOrderId('123')
result_dict = json.loads(result)
assert result_dict.get('code') == 0
```
结果
```
['127.0.0.1:20880', '127.0.0.1:20881','127.0.0.1:20882', '127.0.0.1:20883']
127.0.0.1:20882
[..., 'queryOrderDateByOrderId', ...]
{"code":0,"errMsg":null,"object":null}
```
### 直连Dubbo Provider
```python
import json
from dubboz import Service

service = Service(
    registy='127.0.0.1:20880',
    name='com.***.rpc.order.OrderService')  # 连接zk获取服务
print(service.providers)
print(service.provider)
print(service.methods)
result = service.queryOrderDateByOrderId('123')
result_dict = json.loads(result)
assert result_dict.get('code') == 0
```

结果
```
['127.0.0.1:20880']
127.0.0.1:20880
[..., 'queryOrderDateByOrderId', ...]
{"code":0,"errMsg":null,"object":null}
```
