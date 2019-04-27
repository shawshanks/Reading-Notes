## TCP协议及与UDP协议不同之处

1. TCP是一个面向连接的协议.客户端和服务器能够开始发送数据之前,需要先三次握手并创建一个TCP连接. 
2. TCP链接创建完成后,双方只需经由套接字发送数据,而不用像UDP那样将packet丢进套接字之前必须附上一个目的地地址.

## TCP客户端与服务器端TCP链接步骤概述:
客户端
1. 客户端生成套接字
2. 客户端发起三次握手并和服务器一起创建TCP链接

服务器端
1. 客户端创建 被称为"欢迎之门" 的特殊套接字-->本例中的`serverSocket`.
2. 客户端请求和服务器三次握手,类似于敲 "欢迎之门".服务器'listen'听见敲门时,生成一扇新门,即新的套接字,称之为连接套接字`connection Socket`, 专门用于和这个客户端进行通信连接.

<img src="https://github.com/shawshanks/Reading-Notes/blob/master/image/TCP%E5%A5%97%E6%8E%A5%E5%AD%97%E7%BC%96%E7%A8%8B%E5%9B%BE%E7%A4%BA.png">

## TCP客户端编程步骤:
1. 实例化(创建)TCP套接字,通过第二个参数`SOCK_STREAM`指定. 
注意客户端套接字的端口号由操作系统默认指定.
2. 使用`connet()`方法与服务器之前进行`三次握手`,并创建起一条TCP连接.
3. 使用`send(message)`方法发送信息
注意: 连接之后只需发送数据信息就行了,不需要像UDP那样为Packet附上目的地址`sendto(message,(目的主机名,端口号))`.
4. 使用`recv()`方法接收信息
5. 使用`close()`方法关闭套接字

### TCPClient.py
```python 
from socket import *
serveName = '127.0.0.1'
serverPort = 12000

#1.创建套接字
clientSocket = socket(AF_INET, SOCK_STREAM)

#2.三次握手,创建TCP连接
clientSocket.connect((serveName, serverPort))


sentence = input('请输入小写英文句子:')
sentence_byte = sentence.encode('utf-8')

#3. 发送信息
clientSocket.send(sentence_byte)

modifiedSentence_byte = clientSocket.recv(1024)
modifiedSentence = modifiedSentence_byte.decode('utf-8')

print('来自服务器的返回信息:', modifiedSentence)
#4.关闭连接
clientSocket.close()

```
## TCP服务器端编程步骤
### 1. 欢迎之门: 被动套接字(passive socket)

1.1.  创建套接字 
1.2.  bind()指定端口.          使用`bind()`方法为服务器指定端口(标识套接字).
1.3.  listen()监听连接请求.     将次套接字转变为欢迎之门--使用 `listen()`方法等待某个客户敲门
`listen([backlog])`可以设置参数backlog,该参数指明了处于等待连接的最大数目. 如果服务器还没有通过accpet()方法为某个连接创建套接字,那么该连接就会被
压入栈中等待. 但是如果栈中等待的连接超过了该参数设置的最大等待数, 操作系统就会忽略新的连接请求,并推迟后续的三次握手. 该参数最小值为0.

### 2. 主动套接字

2.1. 创建套接字  
2.2  accept()接收连接          使用`accept()`方法,当客户敲门时,创建一个新的`connection`套接字,用于专门和这个客户连接.  
2.3  recv()接收信息            使用`recv()方法`接收信息

### 3. 关闭套接字
 3.1 完成工作后,关闭`connection`连接.  
 3.2 如果后续还要等待其他客户端的连接请求,   那么欢迎之门的套接字保持打开,响应后续客户的敲门.

### TCPServer.py
```python
from socket import *
serverPort = 12000

# 1.1.创建欢迎之门套接字
serverSocket = socket(AF_INET, SOCK_STREAM)

# 1.2  绑定端口
serverSocket.bind(('127.0.0.1', serverPort))

# 1.3 监听客户连接请求
serverSocket.listen(1)
print("服务器已经准备好接收数据")

while True:
    # 2.1 2.2 accept()创建connection套接字,并接受连接
    connectionSocket, addr = serverSocket.accept()
    
    # 2.3 recv()接收信息
    sentence_byte = connectionSocket.recv(1024)
    sentence = sentence_byte.decode('utf-8')
    capitalizeSentence = sentence.upper()
    capitalizeSentence_byte = capitalizeSentence.encode('utf-8')
    connectionSocket.send(capitalizeSentence_byte)
    
    # 6. 关闭连接
    connectionSocket.close()
    print('完成任务,已关闭这条TCP连接')
```
