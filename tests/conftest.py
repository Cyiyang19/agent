import socket
import pytest

@pytest.fixture(autouse=True)
def forbid_external_network(monkeypatch):
    # Windows asyncio socketpair uses localhost internally.
    original = socket.socket.connect
    def checked(sock, address):
        if isinstance(address, tuple) and address[0] in {'127.0.0.1', '::1'}:
            return original(sock, address)
        raise AssertionError('Offline lab attempted an external network connection')
    monkeypatch.setattr(socket.socket, 'connect', checked)
