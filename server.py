#!/usr/bin/python3
# author: zuo
# 2023年02月02日

import sys
import select
import socket

# 1.创建TCP 的socket对象
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.默认ip会自动填写到 '' 中,只有服务端可以不写
addr = ('', 3000)
# bind 参数是元组
s.bind(addr)
s.listen(120)

# 3.创建epoll对象
epoll = select.epoll()

# 4.添加epoll监听
# x.fileno() 获取x文件句柄fd   select.EPOLLIN 事件类型为可读
epoll.register(s.fileno(), select.EPOLLIN)  # 监听是否有 客户端连入
epoll.register(sys.stdin.fileno(), select.EPOLLIN)  # 监听标准输入 input()

client_list = []  # 存储所有的client对象
timeout = -1
while True:
    # 谁的缓冲区有数据，就填写到events,events是列表里边存的是元组->（fd,事件）
    # epoll.poll(timeout) timeout默认为-1，表示一直监听 直到文件句柄有变化
    events = epoll.poll(timeout)

    for fd, event in events:
        if fd == s.fileno():
            # 有客户端连接，就连上，得到客户端new_client，放入列表，注册它
            new_client, new_addr = s.accept()  # accept() -> (socket object, address info)
            client_list.append(new_client)
            epoll.register(new_client.fileno(), select.EPOLLIN)
        else:  # 像其他用户发消息
            remove_client = None  # 断开连接的客户端
            for client in client_list:
                if client.fileno() is fd:
                    # 获取客户端 的 输入信息
                    data = client.recv(120)
                    if data:
                        for other_client in client_list:  # 除了发信息的客户端，要向其他所有的客户端转发信息
                            if other_client.fileno() is not fd:
                                other_client.send(data)  # 不用转码  本来就是字节流
                    else:  # 该客户端的连接断开了
                        remove_client = client
                        pass
            if remove_client:
                client_list.remove(remove_client)
                epoll.unregister(remove_client.fileno())
                remove_client.close()  # 关闭连接

s.close()
