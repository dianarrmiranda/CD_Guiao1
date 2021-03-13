"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from datetime import datetime


class Message:
    """Message Type."""

    
class JoinMessage(Message):
    """Message to join a chat channel."""


class RegisterMessage(Message):
    """Message to register username in the server."""

    
class TextMessage(Message):
    """Message to chat with other clients."""


class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""


    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""


    @classmethod
    def send_msg(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""


    @classmethod
    def recv_msg(cls, message: str) -> Message:
        """Receives a message and casts to a CDProtocol Message object."""


class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""
