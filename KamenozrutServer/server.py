import socket
from threading import Thread
import re
import json
from db import nickname_exists, add_active_user, init_db, remove_active_user
from datetime import datetime
import pytz

HOST = "127.0.0.1"
PORT = 5555

clients = []
waiting_players = []
matches = {}


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
    nickname = None
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
                        nickname = handle_message(conn, msg, addr)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {addr}: {line}")
    except Exception as e:
        print(f'Failed to connect. {e}')
    finally:
        print(f"Player {addr} disconnected from the server.")
        # TODO: if invalid JSON comes, this will break
        if nickname:
            remove_active_user(nickname)
            # waiting_players.remove((nickname, conn))
        conn.close()


def handle_message(conn, message, addr):
    global waiting_players, matches
    message_type = message["type"]
    nickname = message["data"]["nickname"]
    if message_type == "CHECK_NICKNAME":
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
        waiting_players.append((nickname, conn))
        print(waiting_players)
        if len(waiting_players) >= 2:
            (nick1, player1) = waiting_players.pop(0)
            (nick2, player2) = waiting_players.pop(0)

            bratislava_tz = pytz.timezone("Europe/Bratislava")
            start_time = datetime.now(bratislava_tz).isoformat()
            duration = 180

            room_id = f"{nick1}_{nick2}_{start_time}"
            matches[room_id] = {"player1": {
                "nickname": nick1,
                "conn": player1,
                "score": 0,
                "finished": False,
                "reason": None
            },
                "player2": {
                    "nickname": nick2,
                    "conn": player2,
                    "score": 0,
                    "finished": False,
                    "reason": None
                },
                "start_time": start_time,
                "duration": duration,
                "game_over": False}

            # matches[nick1] = (nick2, player2)
            # matches[nick2] = (nick1, player1)
            player1.sendall(json.dumps({
                "type": "MATCH_FOUND",
                "role": "player1",
                "opponent": nick2,
                "room_id": room_id,
                "start_time": start_time,
                "duration": duration
            }).encode("utf-8") + b"\n")
            player2.sendall(json.dumps({
                "type": "MATCH_FOUND",
                "role": "player2",
                "opponent": nick1,
                "room_id": room_id,
                "start_time": start_time,
                "duration": duration
            }).encode('utf-8') + b"\n")

            # game_start_message = json.dumps({
            #     "type": "GAME_START",
            #     "start_time": start_time,
            #     "duration": duration
            # }).encode("utf-8") + b"\n"
            #
            # player1.sendall(game_start_message)
            # player2.sendall(game_start_message)

    elif message_type == "GRID":
        room_id = message["data"]["room_id"]
        game = matches.get(room_id)
        if game["player1"]["nickname"] == nickname:
            opponents_conn = game["player2"]["conn"]
        else:
            opponents_conn = game["player1"]["conn"]
        opponents_conn.sendall((json.dumps({
            "type": "OPPONENTS_GRID",
            "grid": message["data"]["grid"],
            "color_scheme": message["data"]["color_scheme"]}) + "\n").encode("utf-8"))
    elif message_type == "MOVE":
        room_id = message["data"]["room_id"]
        game = matches.get(room_id)
        if game["player1"]["nickname"] == nickname:
            opponents_conn = game["player2"]["conn"]
        else:
            opponents_conn = game["player1"]["conn"]
        opponents_conn.sendall((json.dumps({
            "type": "MOVE",
            "move": message["data"]["square_description"]}) + "\n").encode("utf-8"))

    elif message_type == "GAME_END":
        room_id = message["data"]["room_id"]
        won = message["data"]["won"]
        score = message["data"]["score"]
        game = matches.get(room_id)
        if game["player1"]["nickname"] == nickname:
            game["player1"]["finished"] = "True"
            game["player1"]["score"] = score
            if won:
                game["player1"]["reason"] = "Won"
            else:
                game["player1"]["reason"] = "No moves left"
            print(game["player1"])
        else:
            game["player2"]["finished"] = "True"
            game["player2"]["score"] = score
            if won:
                game["player2"]["reason"] = "Won"
            else:
                game["player2"]["reason"] = "No moves left"
            print(game["player2"])
    # TODO: each JSON message has to contain nickname in order to work with db
    return nickname


def is_valid_nickname(nickname):
    if nickname is None or len(nickname) == 0:
        return False
    elif not re.match(r"^[A-Za-z0-9_]{1,15}$", nickname):
        return False
    else:
        return True
