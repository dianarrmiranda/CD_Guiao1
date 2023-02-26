"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from socket import socket

class Message:
    """Message Type."""

class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self, channel):
        self.channel = channel

    def __str__(self):
        return f"JOIN {self.channel}"
        

class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"REGISTER {self.username}"

    
class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self, message, channel=None):
        self.message = message
        self.channel = channel

    def __str__(self):
        if self.channel:
            return f"MESSAGE {self.channel} {self.message}"
        else:
            return f"MESSAGE {self.message}"


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
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage(message, channel)

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        msg_str = str(msg)
        data = bytes(msg_str, "utf-8")
        connection.sendall(data)

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        data = connection.recv(2)
        length = int.from_bytes(data, "big")
        data = connection.recv(length)
        msg_str = data.decode("utf-8")
        msg = json.loads(msg_str)
        if msg["command"] == "register":
            return RegisterMessage(msg["user"])
        elif msg["command"] == "join":
            return JoinMessage(msg["channel"])
        elif msg["command"] == "message":
            return TextMessage(msg["message"], msg["ts"])
        else:
            raise CDProtoBadFormat(msg_str)
    

class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
