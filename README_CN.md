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

## 使用
```python
from dubboz import Dubbo

conn = Dubbo('<ip>', <port>)
dict_data = {"class": "类型", "kw1": "value1", ...}
result, elapsed = conn.invoke("<service>", "<method>", dict_data)
```
```python
from dubboz import Service

service = Service('dubbo://127.0.0.1:20880', 'com.longteng.autotest.AnimalService')
print(service.methods)  # 返回方法中所有方法列表
print(service.listAnimals())  # 返回字符串格式的调用结果
print(service.call('listAnimals'))  # 返回字符串格式的调用结果和耗时（单位ms)
print(service.call_all('listAnimals'))  # 返回所有zookeeper所有providers中的调用结果列表，每项包含调用结果和耗时
```
执行结果
```
['getAnimalInfo', 'delAnimal', 'listAnimals', 'addAnimal', 'updateAnimalInfo']
[]
('[]', 0)
[('[]', 0)]
```