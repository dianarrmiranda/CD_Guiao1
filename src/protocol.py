import json
from socket import socket
from datetime import datetime


class Message:
    """Message Type."""
    
    def __init__(self, command):
        self.command = command
    
    def to_json(self):
        raise NotImplementedError


class JoinMessage(Message):
    """Message to join a chat channel."""
    
    def __init__(self, channel):
        super().__init__("join")
        self.channel = channel
    
    def to_json(self):
        return json.dumps({"command": self.command, "channel": self.channel}) #converte python para JSON
    
    def __str__(self):  
        return self.to_json()


class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, user):
        super().__init__("register")
        self.user = user
    
    def to_json(self):
        return json.dumps({"command": self.command, "user": self.user })
    
    def __str__(self):
        return self.to_json()


class TextMessage(Message):
    """Message to chat with other clients."""
    
    def __init__(self, message, channel: str = None, ts=None):
        super().__init__("message")
        self.message = message
        self.channel = channel
        self.ts = ts or int(datetime.now().timestamp())
    
    def to_json(self):
        if self.channel:
            return json.dumps({"command": self.command, "message": self.message,"channel": self.channel, "ts": self.ts })
        else:
            return json.dumps({"command": self.command, "message": self.message, "ts": self.ts })
    
    def __str__(self):
        return self.to_json()


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return RegisterMessage(username)

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage(channel)

    @classmethod
    def message(cls, message: str, channel: str = None, ts=None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage(message, channel, ts)

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        msg_json = msg.to_json().encode("utf-8")
        msg_len = len(msg_json)
        header = msg_len.to_bytes(2, "big") #define o tamanho da mensagem
        connection.sendall(header + msg_json) #sendall garante que a mensagem é enviada completamente

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        # Lê os 2 bytes do cabeçalho
        header = connection.recv(2)
        if not header:
            raise ConnectionError("Connection closed by peer")
        msg_len = int.from_bytes(header, "big") #converte os bytes para inteiro
        msg_json = connection.recv(msg_len).decode("utf-8") # converrte a mensagem de JSON para string

        #verfica se consegue descodificar a mensagem
        try:
            msg_data = json.loads(msg_json)
        except json.JSONDecodeError:
            raise CDProtoBadFormat(msg_json)
        
        if msg_data["command"] == "register":
            return RegisterMessage(msg_data["user"])
        elif msg_data["command"] == "join":
            return JoinMessage(msg_data["channel"])
        elif msg_data["command"] == "message":
            return TextMessage(msg_data["message"], msg_data.get("channel"), msg_data.get("ts"))
        else:
            raise CDProtoBadFormat(msg_json)
        
class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes = None):
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
