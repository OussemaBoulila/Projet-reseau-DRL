import socket
import threading
import pickle

def start_server(host="0.0.0.0", port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(2)
    print(f"🛡️  Server listening on {host}:{port}…")

    connections = []

    def threaded_client(conn, addr):
        connections.append(conn)
        print(f"➡️  Connected: {addr}")
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                for c in connections:
                    if c is not conn:
                        c.send(data)
            except Exception as e:
                print("🔌 Connection error:", e)
                break

        conn.close()
        connections.remove(conn)
        print(f"❌ Disconnected: {addr}")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=threaded_client, args=(conn, addr), daemon=True)
        t.start()
