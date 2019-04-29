# Asynchronous I/O driven directly by the poll() system call.

"""
代码特点:
1. 维护了一个 socket字典, 将socket和其文件描述符关联起来. 然后之后的addresses
字典将socket和其地址联系起来.这样便于查询.
2. 使用自己的数据结构(字典)来维护每个客户端的会话状态,而没有依赖操作系统在客户端改变时
进行上下文切换. 这两个字典 betes_received 和 bytes_to_send 构成了这个移步服务器的
缓冲区.
"""

"""
执行逻辑:
完整状态机,
开始, 客户端将连接请求标志为 event, 并 register,服务器相应给出listener,然后进入服务
器套接字状态.

服务器端套接字有4个状态:
1. 新的监听套接字状态 sock is listener
表示又有又有新的客户端连接请求.
处理: 使用accept()创建新的connect socket ,用于接收这个新的客户端连接

2. 接收状态 POLLIN
处理:
2.1 接收的数据为空 -- 标志为错误或结束, 下次查询时进入 错误或结束状态
2.2 接收到完整的数据 --处理信息,并标记为发送状态 POLLOUT
2.3 没有接收到完整的数据 -- 不改变状态,并等待下次查询,继续接收数据

3. 发送状态 POLLOUT
处理:
3.1 发送了全部的数据 -- 标志为结束
3.2 发送了部分数据 -- 不改变状态,并等待下次查询,继续发送数据

4. 错误或结束状态
处理: 从套接字字典中移除这个套接字, 此次连接结束
"""

import select, zen_utils


def all_events_forever(poll_object):    # 两层循环
    while True:                         # 第一层循环不停地调用poll()来获取事件
                                        # 一个poll()调用可能会返回多个事件
        for fd, event in poll_object.poll():  # 第二层循环用于处理poll()返回的
            yield fd, event                   # 每一个事件


def server(listener):
    # 获取已经准备好进行后续通信的文件描述符,并放入字典中以便之后查询
    sockets = {listener.fileno(): listener}  # 获取监听套接字的文件描述符

    addresses = {}  # 用于保存每个与客户端连接的专用套接字

    # 在等待某个请求完成时, 会将收到的数据存储在bytes_received字典中
    bytes_received = {}

    # 在等待OS安排发送数据时,将要发送的字节存储在bytes_to_send字典中
    bytes_to_send = {}

    poll_object = select.poll()
    # select.poll() 返回一个polling对象,支持registering和unregistering file
    # descriptors, 然后 polling them for I/O events.

    poll_object.register(listener, select.POLLIN)
    # (1)准备连接的客户端首先将它自身视作服务器监听套接字的一个事件,要始终将该事件
    # 设为POLLIN(poll in)状态. 接下来见 elif sock is listener:行注释


    for fd, event in all_events_forever(poll_object):
        sock = sockets[fd]

        # Socket closed: remove it from our data structures.

        if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
            # (5) 如果客户端套接字返回了错误信息或者是关闭状态,就将该客户端套接字及其
            # 发送缓冲区域接收缓冲区丢弃. 至此,我们至少已经完整地完成了众多可能同时
            # 进行的会话中的一个

            # POLLHUP: hung up 挂起
            # POLLERR: Error condition of some sort 错误条件
            # POLLNVAL: invalid request: descriptor not open 无效请求

            address = addresses.pop(sock)
            rb = bytes_received.pop(sock, b'')
            sb = bytes_to_send.pop(sock, b'')
            if rb:
                print('Client {} sent {} but then closed'.format(address, rb))
            elif sb:
                print('Client {} closed before we sent {}'.format(address, sb))
            else:
                print('Client {} closed socket normally'.format(address))
            poll_object.unregister(fd)
            # 移除文件描述符
            del sockets[fd]

        # New socket: add it to our data structures.

        elif sock is listener:
            # (1) 响应此类事件的方法就是运行accept().将返回的套接字及其地址存储在字典内,
            # 并通过register()方法告知poll()对象,已经准备好从新返回的客户端套接字
            # 接收数据了.
            sock, address = sock.accept()
            print('Accepted connection from {}'.format(address))
            sock.setblocking(False)     # force socket.timeout if we blunder
            sockets[sock.fileno()] = sock
            addresses[sock] = address  # 将服务器分配的用于和客户端连接的套接字
                                       # 关联起来并存储在字典中.
            poll_object.register(sock, select.POLLIN)   # 准备好接收数据

        # Incoming data: keep receiving until we see the suffix

        elif event & select.POLLIN:
            # (2)当套接字本身就是客户端套接字,并且时间类型为POLLIN时,就能使用recv()
            # 方法最多接收4KB数据了.
            more_data = sock.recv(4096)

            # 如果没有收到数据, 表示客户端发送的是 b'',客户端结束连接.那么服务器
            # 也要关闭这个与相应客户端连接的套接字. 然后继续下次循环.
            if not more_data:   # end-of-file
                sock.close()    # next poll() will POLLNVAL , and thus clean up
                continue
            data = bytes_received.pop(sock, b'') + more_data

            # 收到了一个完整的问题,可以处理该客户端请求,并将结果保存到bytes_received
            # 字典中. 然后将套接字的模式从POLLIN 切换到POLLOUT. POLLIN模式表示要接收
            # 更多的数据,而POLLOUT模式则表示在发送缓冲区空闲时立刻通知系统 .
            # POLLOUT mode, where you want to be notified as soon as the
            # outgoing buffers are free because you are now using the socket
            # to send instead of receive.
            if data.endswith(b'?'):
                bytes_to_send[sock] = zen_utils.get_answer(data)
                poll_object.modify(sock, select.POLLOUT)
            else:
                # 如果还没有收到表示帧尾的问号字符,那么就将数据保存到 bytes_received
                # 字典中, 并返回至循环顶部,进行下一个poll()调用.
                bytes_received[sock] = data

        # Socket ready to send: keep sending until all bytes are delivered.

        elif event & select.POLLOUT:
            # (3) The poll() call now notifies you immediately with POLLOUT
            # whenever the outging buffers on the client socket can accept
            # at least one byte, and you respond by attempting a send() of
            # everything you have left to transmit and by keeping only the
            # bytes that  send() could not squeeze into the outgoing buffers.
            data = bytes_to_send.pop(sock)
            n = sock.send(data)
            if n < len(data):
                bytes_to_send[sock] = data[n:]
            else:
                # (4)如果套接字模式为POLLOUT, 并且send()完成了所有数据的发送, 那么
                # 此时就完成了一个完整的请求-响应循环, 因此套接字将模式切换回POLLIN,
                # 用于下一个请求.
                poll_object.modify(sock, select.POLLIN)


if __name__ == '__main__':
    address = zen_utils.parser_command_line('low-level async server')
    listener = zen_utils.create_srv_socket(address)
    server(listener)





