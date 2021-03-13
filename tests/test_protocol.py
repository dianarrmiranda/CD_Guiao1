"""Tests for the chat protocol."""
import pytest
from src.protocol import (
    CDProto,
    TextMessage,
    JoinMessage,
    RegisterMessage,
    CDProtoBadFormat,
)

from datetime import datetime
from freezegun import freeze_time


@freeze_time("Mar 16th, 2021")
def test_protocol():
    p = CDProto()

    assert str(p.register("student")) == '{"user": "student"}'

    assert str(p.join("#cd")) == '{"channel": "#cd"}'

    assert (
        str(p.send_msg("Hello World")) == '{"message": "Hello World", "ts": 1615852800}'
    )

    assert isinstance(CDProto.recv_msg(b'{"user": "student"}'), RegisterMessage)
    assert isinstance(CDProto.recv_msg(b'{"channel": "#cd"}'), JoinMessage)
    assert isinstance(
        CDProto.recv_msg(b'{"message": "Hello World", "ts": 1615852800}'), TextMessage
    )

    with pytest.raises(CDProtoBadFormat):
        CDProto.recv_msg(b"Hello World")
