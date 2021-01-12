# Dubboz
简单易用的Dubbo客户端

## install
```.sh
pip install dubboz 
```

## use
```python
from dubboz import Dubbo

conn = Dubbo('<ip>', <port>)
dict_data = {"class": "类型", "kw1": "value1", ...}
result = conn.invoke("<service>", "<method>", dict_data)
```
