import socket
import ssl
import json
import server

from config import *

# Create SSL context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

# Load certificate and key
context.load_cert_chain(certfile="server.crt", keyfile="server.key")

# Create TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to IP and port
sock.bind((SERVER_HOST, TLS_PORT))

sock.listen(5)

print(" TLS control server running")

while True:
    client_sock, addr = sock.accept()

    # Wrap socket with TLS
    secure_sock = context.wrap_socket(client_sock, server_side=True)

    data = secure_sock.recv(1024)
    request = data.decode().strip()

    print("Secure message:", request)

    if request == "GET_RESULTS":
        response = {
            "votes": server.votes,
            "packet_loss_percent": round(server.stats.packet_loss(), 2)
        }
        secure_sock.send(json.dumps(response).encode())
    else:
        secure_sock.send("Hello from TLS Server".encode())

    secure_sock.close()