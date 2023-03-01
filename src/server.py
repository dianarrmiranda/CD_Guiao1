"""CD Chat server program."""

import logging
import selectors
import socket
from .protocol import CDProto

logging.basicConfig(filename="server.log", level=logging.DEBUG)


class Server:
    """Chat Server process."""

    def __init__(self):
        """Initializes chat server."""
        self.host = "localhost"
        self.port = 5000
        self.channels = {}
        self.sel = selectors.DefaultSelector()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(100)
        self.userActual = ""
        self.channelActual = ""

    def accept(self, sock, mask):
        (conn, addr) = sock.accept()  # Should be ready
        logging.debug('Accepted connection from %s ', addr)
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)
        

    def read(self, conn, mask):
        message  = CDProto.recv_msg(conn) #recebe a mensagem
        logging.debug('Accepted message %s ',message)
        print("m: " + str(message))
        if message:
            print("comand: " + message.command)
            if message.command == "register":
                print("Add User " + message.user)
                self.userActual = message.user
                self.channels[message.user] = []
            elif message.command == "join":
                print("Join User " + self.userActual)
                self.channelActual = message.channel
                self.channels[self.userActual].append(message.channel)
            elif message.command == "message":
                for user in self.channels.keys():
                    if self.channelActual in self.channels[user]:
                        print("Message " + str(message.message))
                        CDProto.send_msg(conn, message)
                    else:
                        logging.debug('User %s not in channel', user)
                        print("User " + user + " not in channel")       
            else:
                logging.error('Unknown command %s ',message.command)
            return
        else:
            self.sel.unregister(conn)
            conn.close()
            logging.debug('Closed connection')


    def loop(self):
        """Loop indefinetely."""
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)
        while True:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
