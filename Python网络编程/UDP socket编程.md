<<计算机网络自顶向下方法>>2.7.1 UDP套接字编程


<img src="https://github.com/shawshanks/Reading-Notes/blob/master/image/UDP%E5%A5%97%E6%8E%A5%E5%AD%97%E7%BC%96%E7%A8%8B.png" width = "80%">


## 1.UDP客户端套接字编程步骤:
1. 实例化(创建)一个套接字 socket

2. 使用套接字发送信息 `sorket.sendto()`
包括 data和(目的主机的地址,端口号) 
套接字有四个部分: 源主机地址,源端口号(标识源进程及其套接字) 目的主机地址,目的端口号(标识目的进程及其套接字)
源主机地址和源端口号**默认由操作系统自动处理**

3.接收信息及处理 `socket.recvfrom()`

4. 关闭套接字

### 客户端  UDPClient.py
```python

from socket import *    # 导入socket 模块--Python中网络通信的所有基础

serverName = '127.0.0.1'     # 服务器(目的主机)的IP地址或者主机名的字符串(自动查询DNS从而得到IP地址)
serverPort = 12000          # 目的套接字的端口


# 1客户端创建套接字
clientSocket = socket(AF_INET, SOCK_DGRAM)   # 创建客户端的套接字 
                                            # AF_INET指定了地址簇,特别是,AF_INET指示了底层网路哦使用了IPv4
                                            # SOCK_DGAM指定套接字是SOCK_DGARM类型,即UDP套接字
                                            # 客户端套接字的端口号不指定的话,操作系统默认为我们生成
                                            
message_str = input("Input lowercase sentence:")# 要发送的信息
message_byte = message_str.encode('utf-8')  # 将发送的信息编码成字节串,网络中传送的是字节而不是字符串


# 2创建datagram(packet),然后使用Socket的sendto()方法向目的主机进程发送套接字
clientSocket.sendto(message_byte, (serverName, serverPort))  # 发送进程为分组附上 目的地址(目的主机的IP地址,目的套接字-->属于运输层)
                                                        # 默认由OS为分组附上 源地址(发送主机的IP地址, 源套接字-->运输层)
                                                        # 方法sendto()为报文附上目的地地址(serverName,serverPort)
                                                        
                                                        
# 3从clientSocket 读取来自目的主机进程发送的datagram(数据报)                                                        
modifiedmessage, serverAddress = clientSocket.recvfrom(2048) # 一旦接收到一个数据报,recvfrom()方法返回两个值
                                                             # 第一个是发送该数据报的地址 ,该地址被放到了变量serverAddress中,包含了服务器的IP地址和端口号
                                                             # 第二个是以字节表示的数据报内容,,数据报内容被放在了modifiedmessage中
                                                             # 取缓存2048作为输入
                                                             
print(modifiedmessage.decode('utf-8'))  # 将接收到的字节串解码成字符串

# 4 关闭套接字
clientSocket.close()
 ```
 
 ## 2.服务器端套接字编程步骤
 
 1. 实例化(创建)一个套接字
 2. 为服务器套接字绑定(分配)一个端口号
 3. 循环接受服务
    - 接收信息 `recvfrom()方法`
    - 处理信息
    - 发送信息`sendto()方法`
    
 ### 服务器端  UDPServer.py
 ```python
 from socket import *

serverPort = 12000

# 创建套接字
serverSocket = socket(AF_INET, SOCK_DGRAM)

# 将端口12000和服务器主机127.0.0.1绑定,即显式地为该套接字分配一个端口号
serverSocket.bind(('127.0.0.1', serverPort))      # 以这种方式,当任何人向该主机的端口发送数据报,该数据报将指向这个套接字
print("The server is ready to receive")

while True:
    
    message_byte, clientAddress = serverSocket.recvfrom(2048) # 当某个packet到底该服务器的套接字时,该packet的数据被发到变量message_byte中
                                                              # 源地址被放到变量clientAddress中,包含源地址的IP和套接字端口号
    
    message_str = message_byte.decode('utf-8')                # 解码成字符串
    modifiedMessage = message_str.upper()                     # 转换成大写
    modifiedMessage_byte = modifiedMessage.encode('utf-8')    # 编码成字节串
    serverSocket.sendto(modifiedMessage_byte, clientAddress)       # 发送数据内容编码成字节串的packet
    
 ```
