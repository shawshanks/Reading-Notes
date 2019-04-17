[Linux Socket编程（不限Linux）](http://www.cnblogs.com/skynet/archive/2010/12/12/1903949.html)  
[socket实现原理和机制](https://www.cnblogs.com/airtcp/p/5230161.html)


<<计算机网络自顶向下方法>>2.7.1 UDP套接字编程
```python
from socket import *    # 导入socket 模块--Python中网络通信的所有基础

serverName = 'hostname'     # 服务器(目的主机)的IP地址或者主机名的字符串(自动查询DNS从而得到IP地址)
serverPort = 12000          # 目的套接字的端口


# 1客户端创建套接字
clientSocket = Socket(AF_INET, SOCK_DGAM)   # 创建客户端的套接字 
                                            # AF_INET指定了地址簇,特别是,AF_INET指示了底层网路哦使用了IPv4
                                            # SOCK_DGAM指定套接字是SOCK_DGARM类型,即UDP套接字
                                            # 客户端套接字的端口号不指定的话,操作系统默认为我们生成
                                            
message = input("Input lowercase sentence:")# 要发送的信息


# 2创建datagram(packet),然后使用Socket的sendto()方法向目的主机进程发送套接字
clientSocket.sendto(message, (serverName, serverPort))  # 发送进程为分组附上 目的地址(目的主机的IP地址,目的套接字-->属于运输层)
                                                        # 默认由OS为分组附上 源地址(发送主机的IP地址, 源套接字-->运输层)
                                                        # 方法sendto()为报文附上目的地地址(serverName,serverPort)
                                                        
                                                        
# 3从clientSocket 读取来自目的主机进程发送的datagram(数据报)                                                        
modifiedmessage, serverAddress = clientSocket.recvfrom(2048) # 一旦接收到一个数据报,recvfrom()方法返回两个值
                                                             # 第一个是发送该数据报的地址 ,该地址被放到了变量serverAddress中,包含了服务器的IP地址和端口号
                                                             # 第二个是以字节表示的数据报内容,,数据报内容被放在了modifiedmessage中
                                                             
print(modifiedmessage)

# 4 关闭套接字
clientSocket.close()

 ```
