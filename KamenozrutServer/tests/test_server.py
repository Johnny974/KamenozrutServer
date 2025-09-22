import socket
import threading
import time
import pytest
import json

import server


@pytest.fixture(scope="module")
def run_server():
    thread = threading.Thread(target=server.start_server, daemon=True)
    thread.start()
    time.sleep(0.5)
    yield


def send_and_receive(msg: dict):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server.HOST, server.PORT))
    s.sendall((json.dumps(msg) + "\n").encode("utf-8"))
    data = s.recv(1024).decode("utf-8")
    s.close()
    return data.strip()


def test_invalid_nickname(run_server):
    response = send_and_receive({
        "type": "CHECK_NICKNAME",
        "data": {"nickname": "!!!"}
    })
    resp_json = json.loads(response)
    assert resp_json["type"] == "NICKNAME_INVALID"


def test_valid_nickname(run_server):
    response = send_and_receive({
        "type": "CHECK_NICKNAME",
        "data": {"nickname": "Player1"}
    })
    resp_json = json.loads(response)
    assert resp_json["type"] in ["NICKNAME_OK", "NICKNAME_TAKEN"]