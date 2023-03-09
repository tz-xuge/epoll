#!/usr/bin/python3
# author: zuo
# 2023年02月02日

import select
import socket
import sys

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest_addr = ('39.101.64.116', 3000)
client.connect(dest_addr)
epoll = select.epoll()  # 创建一个epoll对象
epoll.register(client.fileno(), select.EPOLLIN)
epoll.register(sys.stdin.fileno(), select.EPOLLIN)

while True:
    # 谁的缓冲区有数据，就填写到events
    events = epoll.poll(-1)
    for fd, event in events:
        if fd == client.fileno():
            data = client.recv(100)
            if data:
                print(data.decode('utf8'))

        elif fd == sys.stdin.fileno():
            data = input()
            client.send(data.encode('utf8'))
client.close()
