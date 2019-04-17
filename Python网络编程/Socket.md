[Linux Socket编程（不限Linux）](http://www.cnblogs.com/skynet/archive/2010/12/12/1903949.html)  
[socket实现原理和机制](https://www.cnblogs.com/airtcp/p/5230161.html)

## 进程与套接字
进程通过一个称为**套接字**的软件接口向网络发送message和从网络接收message.

进程可以类比于一座房子,而进程的套接字可以类比于这座房子的门. 当一个进程想向位于另外一台主机上的另一个进程发送报文时,这个进程把message推出门. 进程之间假定两座房子之间有运输的基础设施,会把message运输到门口.然后接收message的进程通过自己的门(socket)接收message.

Socket是主机上应用层和运输层之间的接口,也称为应用程序编程接口(Application Programming Interface,API)

## 套接字编程步骤
1. 实例化一个套接字 socket
2. 使用套接字发送信息 sorket.sendto() 包括 data和(目的主机的地址,端口号) 
套接字有四个部分: 源主机地址,源端口号(标识源进程及其套接字)  目的主机地址,目的端口号(标识目的进程及其套接字)  
源主机地址和源端口号默认由操作系统自动处理
3. 接收信息及处理  socket.recvfrom()
4. 关闭套接字

## 开发者使用套接字的权限
开发者可以控制套接字在应用端的一切,但是对于该套接字的运输层端几乎没有控制权.  
开发者对于运输层的控制仅限于: 1 选择运输层协议(TCP/UDP)  2 也许能设定几个运输层参数,如最大缓存和最大报文长度


## 运输层所提供的服务
### 称呼问题
在与互联网有关的环境中,我们将运输层的packet称之为segment(报文段)  
而互联网文献(如RFC文档)也将transport-layer packet for TCP (Transmission Control Protocol) 称为 segment(报文段)  
                       将transport-layer packet for UDP(User Datagram Protocol)称为 datagram(数据报)
                       
但是这些互联网文献同时也将网络层Packet称为datagram(数据报)

### 运输层提供的服务
运输层UDP和TCP的最基本责任是: 将主机间信息交付 扩展到 进程间信息交付.

运输层接收到网络层的信息后, 并没有直接把数据交付给进程,而是将数据交给了一个中间的套接字. 由于接受主机上可能不止有一个套接字,所以用**端口号**来标识套接字.

运输层从源主机的不同套接字中收集数据块,并为每个数据块封装上首部信息(之后用作分解),从而生成 segment(报文段),然后将报文段传递到网络层. 所有的这些工作
称为**mutilplexing(多路复用)**  

#### plex
词源: From the Latin past tense of plectere (“to weave(编,织), braid(头发梳成辫子), twine(绳子拧成两股或多股的线), entwin盘绕”).
-plex后缀意思 Comprising a number of parts, as in duplex.
所以 mutilplexing 翻译成 **多次组合** 比较符合原意.

而运输层 检查 从网络层接收到的datagram中的字段,标识出套接字,然后将拆分出的segment(报文段)交付给正确的套接字. 这些工作称之为**demultiplexing(多路分解)** .同样,我认为称之为 **多次分解** 比较符合英文原意.


## UDP和TCP报文段segment结构
3.3.1 图
## UDP套接字
一个UDP套接字由 一个二元元组来标识 即(目的IP地址,目的端口号).

如果两个UDP 报文段有不同的源IP地址或源端口号,但是具有相同的*目的IP地址*和*目的端口号*,那么这两个报文段将通过相同的目的套接字被交给相同的目的进程.
