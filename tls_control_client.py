import socket
import ssl

from config import *
from protocol import *

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

sock = socket.socket()
secure = context.wrap_socket(sock, server_hostname="localhost")

secure.connect((SERVER_HOST, TLS_PORT))
secure.send(create_results_request().encode())

data = secure.recv(BUFFER_SIZE)
print("Secure Results:", data.decode())

secure.close()