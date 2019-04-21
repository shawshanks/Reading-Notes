[getaddrinfo官方文档](https://docs.python.org/zh-cn/3/library/socket.html#creating-sockets)
>Translate the host/port argument into a sequence of 5-tuples that contain all the necessary arguments for creating a socket 
connected to that service. 

```python
>>> socket.getaddrinfo("example.org", 80, proto=socket.IPPROTO_TCP)
[(<AddressFamily.AF_INET6: 10>, <SocketType.SOCK_STREAM: 1>,
 6, '', ('2606:2800:220:1:248:1893:25c8:1946', 80, 0, 0)),
 (<AddressFamily.AF_INET: 2>, <SocketType.SOCK_STREAM: 1>,
 6, '', ('93.184.216.34', 80))]
```

使用方法:
1. 提供所需链接的服务器 (域名+端口号) "example.org", 80
2. 返回一个元组列表.每个列表都表示一种链接到服务器的方法(IP4 or IP6)
3. 创建链接方法:
- 选中结果中的一个列表  

`infolist =  socket.getaddrinfo("example.org", 80, proto=socket.IPPROTO_TCP)`

`info = infolist[0]     `                 
- 提取创建套接字的所需信息 并创建套接字

`s = socket.socket(*info[0:3])`

- 链接服务器 (列表中的最后一项就是服务器的(IP地址+端口)**IP4**

`s.connect(info[4])`
