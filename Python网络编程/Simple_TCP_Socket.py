# Simple TCP client and server that send and receive 16 octets(8位的字节)

import argparse, socket

def recvall(sock, length):
    data = b'' 
    
    # https://docs.python.org/zh-cn/3/reference/lexical_analysis.html#string-and-bytes-literals
    # 字节串字面值总是带有前缀 'b' 或 'B'；它们生成 bytes 类型而非 str 类型的实例。
    # 它们只能包含 ASCII 字符；字节对应数值在128及以上必须以转义形式来表示。
    
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('was expecting %d bytes but only received' 
                            '%d bytes before the socket closed'
                            % (length, len(data))) # %d 有符号十进制整数
        data += more
        return data 
        
    
def server(interface, port):
    # 1. 建立套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((interface, port)) 
    sock.listen(1)
    # listen()决定了这个程序要作为服务器,对套接字的改变无法撤销
    # 调用之后该套接字再也不能用于发送或接收数据
    
    print('Listening at', sock.getsockname())
    # getsockname()同时适用于监听套接字和连接套接字,可以用于获取套接字正在使用的绑定TCP端口
    # 如果想获取连接套接字的对应的客户端地址,可以调用getpeername(),也可以存储accpt()方法的
    # 第二个返回只.
    while True:
        print('Waiting to accept a new connection')
        sc, sockname = sock.accept()
        print(2)
        # 1.监听套接字调用accept()后实际会返回一个新建的连接套接字
        
        
        print('We have accepted a connection from', sockname)
        print('    Socket name:', sc.getsockname())
        print('    Socket peer:', sc.getpeername())
        message = recvall(sc, 16)
        
        print('     Incoming sixteen-octet message:', repr(message)) 
        # https://docs.python.org/zh-cn/3/library/functions.html#repr
        # str()用于为终端用户,repr()主要用于debugg和开发repr()的目标是无歧义
        # 而str()的目标是可读性.
        # 查看https://www.geeksforgeeks.org/str-vs-repr-in-python/以获得更详细的解释

        sc.sendall(b'Farewell, client')
        sc.close()
        print('     Reply sent, socket closed')
        
    
def client(host, port):
    # 1. 建立套接字 SOCK_STREAM说明是TCP协议 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2.TCP connect真实的网络链接:三次握手 
    # 客户端进程通知客户端运输层它想和服务器建立链接
    
    # 不同点:UDP的connect()只是对绑定套接字进行了配置,设置了后续send()或recv()
    # 所使用的默认远程地址,不会导致任何错误
    sock.connect((host, port))
    
    
    print('Client has been assigned socket name', sock.getsockname())
    sock.sendall(b'Hi there, server')
    print(1)
    reply = recvall(sock, 16)
    print('The server said', repr(reply))
    sock.close()
    
 
if __name__ == '__main__':
    # 关于parser模块的用法介绍:
    # https://towardsdatascience.com/learn-enough-python-to-be-useful-argparse-e482e1764e05
    choices = {'client':client, 'server':server}
    
    # 1. 创建parser对象
    parser = argparse.ArgumentParser(description='Send and receive over TCP')
    
    # 2. 创建parser对象的位置变量 role
    # 2.1 choics 参数说明role的值只能是choices字典中的值.命令行传入键,Python会选择对应的值作为
    # 变量role的值
    parser.add_argument('role', choices=choices, help='which role to play')
    

    # 2. 创建parser对象的位置变量 host
    parser.add_argument('host', help='interface the server listens at;'
                        'host the client sends to')
                        
    # 2. 创建parser对象的可选参数变量 -p .default=1060说明默认为1060                  
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
                        
    # 3. 变量args被设置为parsed参数的值
    args = parser.parse_args()  
                                
    function = choices[args.role] 
    # 假设我们命令行为 python Sim_TCP_Socket.py server ""
    # 那么 arg.role = server  
    # function = choices[server] = server
    
    function(args.host, args.p) # 效果为 server('0.0.0.0', 1060)
    
    
    