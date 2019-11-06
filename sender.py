#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT =  12000       # The port used by the server
x = input().encode()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
while True:
    s.sendall(x)
    data = s.recv(1024)
    print(data)
    if not data:
        break