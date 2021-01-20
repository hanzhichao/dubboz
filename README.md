# Dubboz
Easy use for dubbo python client

## install
```.sh
pip install dubboz
```

## use
### use zookeeper as registry
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
### use dubbo provider directly
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
