import socket
import time

from config import *
from protocol import *

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(ACK_TIMEOUT)

server = (SERVER_HOST, UDP_PORT)

user = input("Enter User ID: ")

print("1 Python\n2 Java\n3 C++")
choice = input("Choice: ")

vote_map = {"1": "Python", "2": "Java", "3": "C++"}
vote = vote_map.get(choice, "Python")

packet = create_vote_packet(user, vote)

retries = 0

while retries < MAX_RETRIES:
    try:
        client.sendto(packet.encode(), server)
        data, _ = client.recvfrom(BUFFER_SIZE)
        response = parse_packet(data.decode())

        if response["type"] == "ack":
            print("Vote successful!")
            break
        else:
            print(response["message"])
            break

    except socket.timeout:
        retries += 1
        print("Retrying...")

client.close()