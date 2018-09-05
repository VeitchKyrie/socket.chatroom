"""
Created on 2018-8-27
coding: utf-8
@author: aedin
"""

import socket
import select
import threading

client_address = ('10.101.0.38', 9999)

# 监听信息 并打印


def listening(cs):
    inputs = [cs]
    while True:
        rlist, wlist, elist = select.select(inputs, [], [])

        if cs in rlist:
            try:
                print(str(cs.recv(1024), encoding="utf-8"))
            except socket.error:
                print("socket is error")
                exit()

# 输入信息 并发送


def speak(cs):
    data = ""
    while True:
        try:
            data = input()
        except Exception as e:
            print("can't input")
            print(e)
            exit()

        data = bytes(data, encoding="utf-8")
        try:
            cs.send(data)
        except Exception as e:
            print("can't send")
            print(e)
            exit()


def main():
    cs = socket.socket()
    cs.connect(client_address)

    t = threading.Thread(target=listening, args=(cs,))
    t.start()

    t1 = threading.Thread(target=speak, args=(cs,))
    t1.start()


if __name__ == "__main__":
    main()

