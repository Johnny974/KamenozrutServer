import socket
from threading import Thread

HOST = "127.0.0.1"
PORT = 5555

clients = []


def handle_client(conn, addr):
    print(f"[PRIPOJENIE] {addr} sa pripojil.")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Správa od {addr}: {data.decode()}")
    except Exception as e:
        print(f'Failed to connect. {e}')
    finally:
        print(f"[ODPOJENIE] {addr} sa odpojil.")
        conn.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"[SERVER] Server beží na {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        clients.append(conn)
        thread = Thread(target=handle_client, args=(conn, addr))
        thread.start()
