#  Created by Artem Manchenkov
#  artyom@manchenkoff.me
#
#  Copyright © 2019
#
#  Сервер для обработки сообщений от клиентов
#
from collections import deque

import self as self
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        self.factory.clients.append(self)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)
        if self.login in self.factory.List_of_login:
            self.factory.List_of_login.remove(self.login)

    def send_history(self):
        self.sendLine("Last 10 messages:".encode())
        for msg in self.factory.history:
            self.sendLine(msg.encode())

    def lineReceived(self, line: bytes):
        print(f"message: {line}")
        content = line.decode()

        if self.login is not None:

            content = f"Message from {self.login}: {content}"
            self.factory.history.append(content)
            for user in self.factory.clients:
                if user is not self:
                    user.sendLine(content.encode())

        else:
            if content.startswith("login:"):
                self.login = content.replace("login:", "")
                if self.login not in self.factory.List_of_login:
                    self.sendLine("Welcome!".encode())
                    self.send_history()
                    self.factory.List_of_login.append(self.login)
                else:
                    self.sendLine(f"Login {self.login} is already exist, try another login!".encode())
                    self.transport.loseConnection()
            else:
                self.sendLine("Invalid login!".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    List_of_login: list
    history: deque

    def doStart(self):
        print("Server started")
        self.clients = []
        self.List_of_login = []
        self.history = deque(maxlen=10)

    def doStop(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
