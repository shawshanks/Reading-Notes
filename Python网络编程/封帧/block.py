'''
封帧问题:
1. 消息接收方如何知道何时停止调用recv()才不至于消息没接收完.
2. 消息接收方如何知道何时将接受到的消息作为一个整体来解析或处理.

解决方法:
1. 一直接收到收到空字符串为止(表示消息结束),然后处理信息 (警告:一定要先完成一个方向的传送,然后反过来在另一方向上发送数据,否则可能会发生死锁问题)
2. 使用特殊字符来划分消息的边界(当做定界符)
3. 在消息前加上其长度作为前缀,这样消息接收方就知道消息的长度

本程序使用第三个方法
'''


'''
代码逻辑:
1. client发送信息之前,先发送其长度作为前缀.
2. 服务器知道消息长度之后,方便用while循环内,重复用recv()接收一个定长消息.
3. 数据发送完成之后,通信双方可以约定发送完毕信号.然后结束通信
'''

'''
实现细节:
1. 客户端 发送信息长度实现
put_block()中使用 strcut.pack()方法 将 信息长度 编码为字节对象

>>> import struct
>>> block_length = len( b'Beautiful is better than ugly.')
>>> block_lenght
30
>>> head_struct = struct.struct('!I')
>>> head_struct.size
4
>>> head_struct.pack(block_length)
b '\x00\x00\x00\x1e'
>>> len(head_struct.pack(block_length))
4

可见pack()方法将 消息 b'Beautiful is better than ugly.'的长度编码为4个字节,
然后通过send()方法这个4个字节b '\x00\x00\x00\x1e'以二进制格式 发送给服务器.

2. 因为一开始在
`header_struct = struct.Struct('!I')  # message up to 2**32 -1 in length`
中定义了header_struct,所以服务器知道 header_struct的formating character是 !I
即用于网络传输的大端法的4字节无符号整数. 这个可以通过 header_struct.size 查询.
. 然后服务器知道要接收4字节的二进制数据,在while循环内 收到 b '\x00\x00\x00\x1e'
这4个字节的信息. 

3. 服务器按照大端法使用unpack()方法解码二进制字符串,

>>> head_struct.unpack(b'\x00\x00\x00\x1e')
(30,)

服务器于是知道这次将要接收到的信息为30个二进制字节.
'''
# Sending data over a stream but delimited as lenght-prefixed blocks

import socket
import struct
from argparse import ArgumentParser


header_struct = struct.Struct('!I')  # message up to 2**32 -1 in length
# class struct.Struct(format)
'''
Return a new Struct object which writes and reads binary data according to the format string format.
Creating a Struct object once and calling its methods is more efficient than calling the struct functions with the same format
since the format string only needs to be compiled once.
!I 表示用于网络传输的long int.(4bytes)
'''


def recvall(sock, length):
    blocks = []
    while length:
        block = sock.recv(length)
        if not block:
            raise EOFError('socket closed with %d bytes left'
                            ' in this block.'.format(length))
        length -= len(block)    # 需要接收到的长度减去已经收到的长度
        blocks.append(block)    # 把信息存储在列表中
    return b''.join(blocks)     # 拼接信息


def get_block(sock):
    data = recvall(sock, header_struct.size)
    (block_length,) = header_struct.unpack(data)
    return recvall(sock, block_length)


def put_block(sock, message):
    block_length = len(message)
    sock.send(header_struct.pack(block_length))
    sock.send(message)


def server(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(1)
    print('Run this script in another window with "-c" to connect')
    print('Listening at', sock.getsockname())
    sc, sockname = sock.accept()
    print('Accepted connection from', sockname)
    sc.shutdown(socket.SHUT_WR)
    while True:
        block = get_block(sc)
        if not block:
            break
        print('Block says:', repr(block))
    sc.close()
    sock.close()


def client(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    sock.shutdown(socket.SHUT_RD)
    put_block(sock, b'Beautiful is better than ugly.')
    put_block(sock, b'Explicit is better than implicit.')
    put_block(sock, b'Simple is better than complex.')
    put_block(sock, b'')
    sock.close()


if __name__ == '__main__':
    parser = ArgumentParser(description='Transmit & receive blocks over TCP.')
    parser.add_argument('hostname', nargs='?', default='127.0.0.1',
                        help='IP address or hostname (default: %(default)s)')
    parser.add_argument('-c', action='store_true', help='run as the client')
    parser.add_argument('-p', type=int, metavar='port', default=1060,
                        help='TCP port number (default: %(default)s)')
    args = parser.parse_args()
    function = client if args.c else server
    function((args.hostname, args.p))
