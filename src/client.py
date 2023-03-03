"""CD Chat client program"""
import fcntl
import logging
import os
import selectors
import socket
import sys

from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.sock, selectors.EVENT_READ, self.read_message)
        self.connected = False
        self.channel = None

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.sock.connect(("localhost", 5000))
        self.connected = True
        
        regMessage = CDProto.register(self.name)
        CDProto.send_msg(self.sock, regMessage)
        #print("Client ", self.name,"registered")
        
    def read_message(self, conn, mask):
        message = CDProto.recv_msg(conn)  # recebe a mensagem
        if not message:
            logging.debug('Empty message')
        else:
            logging.debug('Received "%s', message)
            print(str(message.message))

    def got_keyboard_data(self, stdin, mask):
        messageIn = stdin.read().rstrip('\n')
        
        if messageIn:
            if messageIn.startswith("/join "):
                self.channel = messageIn[6:]
                print("Channel ", self.channel," join")
                joinUser = CDProto.join(self.channel)
                CDProto.send_msg(self.sock, joinUser)
            elif messageIn == "exit":
                self.sel.unregister(self.sock)
                self.sock.close()
                logging.debug('Closed connection')
            else:
                message = CDProto.message(messageIn, self.channel)
                CDProto.send_msg(self.sock, message)

    def loop(self):
            """Loop indefinetely."""
            orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

            self.sel.register(sys.stdin, selectors.EVENT_READ, self.got_keyboard_data)
            
            while True:
                #sys.stdout.write('Type something and hit enter: ')
                #sys.stdout.flush()
                for k, mask in self.sel.select():
                    callback = k.data
                    callback(k.fileobj, mask)
                
                


                
                
            
