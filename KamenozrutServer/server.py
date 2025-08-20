import socket
from threading import Thread
import re
import json
from db import nickname_exists, add_active_user, init_db

HOST = "127.0.0.1"
PORT = 5555

clients = []


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server runs on {HOST}:{PORT}")
    init_db()
    while True:
        conn, addr = server_socket.accept()
        clients.append(conn)
        thread = Thread(target=handle_client, args=(conn, addr))
        thread.start()


def handle_client(conn, addr):
    print(f"Player {addr} connected to server.")
    buffer = ""
    try:
        while True:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    try:
                        msg = json.loads(line)
                        print(f"JSON from {addr}: {msg}")
                        handle_message(conn, msg, addr)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {addr}: {line}")
    except Exception as e:
        print(f'Failed to connect. {e}')
    finally:
        print(f"Player {addr} disconnected from the server.")
        conn.close()


def handle_message(conn, message, addr):
    message_type = message["type"]
    if message_type == "CHECK_NICKNAME":
        nickname = message["data"]["nickname"]
        if is_valid_nickname(nickname):
            if nickname_exists(nickname):
                response = {"type": "NICKNAME_TAKEN"}
            else:
                add_active_user(nickname, addr[0])
                response = {"type": "NICKNAME_OK"}
        else:
            response = {"type": "NICKNAME_INVALID"}
        conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
    elif message_type == "MATCHMAKING":
        pass


def is_valid_nickname(nickname):
    if nickname is None or len(nickname) == 0:
        return "Nickname is required."
    elif not re.match(r"^[A-Za-z0-9_]{1,15}$", nickname):
        return "Nickname can only contain letters, numbers and underscores."
    else:
        return True
