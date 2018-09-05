"""
Created on 2018-8-30
coding: utf-8
@author: aedin
利用socket网络通信模块 打造一个聊天室
8/30 解决了堵塞的问题 并打包成了类
8/31 加入多线程 一个运行聊天室 一个运行控制台
"""

import socket
import select
import threading
import time


class ChatServer:
    def __init__(self, port, backlog=5):
        self.server = socket.socket()
        self.server.bind(('10.101.0.38', port))
        self.server.listen(backlog)
        self.running = True
        self.clients = 0   # 用户个数
        self.client_map = {}  # 进入聊天室的用户
        self.address_wait = {}  # 连接的客户端 等待区
        self.log = []  # 聊天记录
        self.history = []  # 日志

    def get_client_name(self, client):
        info = self.client_map[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

    @staticmethod
    def get_time():
        return time.asctime(time.localtime(time.time()))

    def broadcast_chat_messages(self, sock, data):
        msg = '<'+self.get_time()+'>\n#[' + self.get_client_name(sock) + '] : ' + data
        self.log.append(msg)
        for other in self.client_map.keys():
            if other != self.server and other != sock:
                other.send(bytes(msg, encoding="utf-8"))

    def broadcast_join_message(self, sock):
        msg = '<'+self.get_time()+'>#Connected: New client from [%s]' % self.get_client_name(sock)
        self.log.append(msg)
        for other in self.client_map.keys():
            if other != self.server and other != sock:
                other.send(bytes(msg, encoding="utf-8"))

    def broadcast_exit_message(self, sock):
        msg = '<'+self.get_time()+'>#Now hung up: Client from [%s]' % self.get_client_name(sock)
        self.log.append(msg)
        for other in self.client_map.keys():
            if other != self.server and other != sock:
                other.send(bytes(msg, encoding="utf-8"))

    # 聊天室主程序
    def working(self):
        inputs = [self.server]
        while self.running:
            try:
                rlist, wlist, elist = select.select(inputs, [], [])
            except select.error as e:
                print(e)
                break

            if not rlist:
                print("timeout...")
                break

            for sock in rlist:
                # 建立连接 并发送连接消息请求昵称
                if sock == self.server:
                    client, address = self.server.accept()
                    # 发送欢迎消息
                    # print("Chat server: got connection %d from %s" % (client.fileno(), address))
                    msg = '<'+self.get_time()+'> got connection %d from %s' % (client.fileno(), address)
                    self.history.append(msg)
                    client.send(bytes("welcome to chat room,pls set up your nick name!\n", encoding="utf-8"))
                    client.send(bytes("NAME: ", encoding="utf-8"))

                    inputs.append(client)
                    self.address_wait[client] = address

                else:  # 表示一个client连接上有数据到达服务器
                    connect = True
                    try:
                        data = str(sock.recv(1024), encoding="utf-8")
                    except socket.error:
                        connect = False
                    else:
                        pass

                    if connect:
                        # 收到消息 并广播到其他客户端
                        if sock in self.client_map:
                            # print(data)
                            self.broadcast_chat_messages(sock, data)

                        # 收到昵称 加入聊天室
                        else:
                            # print(sock)
                            # print("name:"+data)

                            # 发送加入聊天室的消息
                            sock.send(bytes("CLIENT: " + str(self.address_wait[sock][0]), encoding="utf-8"))

                            self.client_map[sock] = (self.address_wait[sock], data)  # 储存昵称
                            self.address_wait.pop(sock)
                            self.clients += 1
                            # 广播用户加入消息
                            self.broadcast_join_message(sock)

                    # 该客户端退出服务器
                    else:
                        # print("Chat server: %d from %s hung up" % (sock.fileno(), str(sock.getpeername())))
                        msg = '<' + self.get_time() + '> %d from %s hung up' % (sock.fileno(), str(sock.getpeername()))
                        self.history.append(msg)
                        if sock in self.client_map:
                            # 广播用户退出消息
                            self.broadcast_exit_message(sock)
                            del self.client_map[sock]
                            self.clients -= 1
                        sock.close()
                        inputs.remove(sock)
        # 关闭服务器 并退出
        self.close()

    def close(self):
        for sock in self.client_map.keys():
            sock.close()
        self.server.close()
        exit()

    def stop(self):
        self.running = False

    @staticmethod
    def console_help():
        print('==============================')
        print("\\q    : exit the program")
        print("\\h    : Ask for help")
        print("\\l    : View client chat logs")
        print("\\s    : View system diary")
        print("\\c    : View connection users")
        print('==============================')

    def console_log(self):
        print('==============================')
        for i in self.log:
            print(i)
        print('==============================')

    def console_history(self):
        print('==============================')
        for i in self.history:
            print(i)
        print('==============================')

    def console_client(self):
        print('==============================')
        for i in self.client_map:
            print(i)
        print('==============================')

    def console_select(self, data):
        if data == "\q":
            self.close()
        elif data == "\h":
            self.console_help()
        elif data == "\l":
            self.console_log()
        elif data == "\s":
            self.console_history()
        elif data == "\c":
            self.console_client()
        else:
            print("\033[31m unknown command ! please input \'\\h\' for help \033[0m")

    # 控制台主程序
    def console_desk(self):
        while self.running:
            try:
                data = input('>> ')
                self.console_select(data)
            except Exception as e:
                print("can't input")
                self.close()


def main():
    server = ChatServer(port=9999, backlog=10)

    t = threading.Thread(target=server.working, args=())
    t.start()

    t1 = threading.Thread(target=server.console_desk, args=())
    t1.start()


if __name__ == "__main__":
    main()
