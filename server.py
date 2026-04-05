import socket
import ssl
import threading
import time
import json

from config import *
from protocol import *
from stats import PacketStats

votes = {}
voted_users = set()
stats = PacketStats()
lock = threading.Lock()

# ================= UDP SERVER =================
udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server.bind((SERVER_BIND_IP, UDP_PORT))


def handle_vote(data, addr):
    stats.received()

    try:
        packet = parse_packet(data.decode())
    except:
        stats.invalid_packet()
        response = create_error_packet("Invalid packet")
        udp_server.sendto(response.encode(), addr)
        return

    if not packet or packet.get("type") != "vote":
        stats.invalid_packet()
        response = create_error_packet("Invalid packet")
        udp_server.sendto(response.encode(), addr)
        return

    try:
        user = packet.get("user")
        vote = packet.get("vote")
    except:
        stats.invalid_packet()
        response = create_error_packet("Invalid packet")
        udp_server.sendto(response.encode(), addr)
        return

    # ✅ Check missing fields
    if not user or not vote:
        stats.invalid_packet()
        response = create_error_packet("Invalid packet")
        udp_server.sendto(response.encode(), addr)
        return

    # ✅ Check valid vote
    if vote not in ["Python", "Java", "C++"]:
        stats.invalid_packet()
        response = create_error_packet("Invalid packet")
        udp_server.sendto(response.encode(), addr)
        return

    with lock:
        # ✅ Duplicate check
        if user in voted_users:
            stats.duplicate()
            response = create_error_packet("Duplicate User")

        else:
            voted_users.add(user)
            votes[vote] = votes.get(vote, 0) + 1
            stats.processed_packet()
            response = create_ack_packet("Vote counted")

    udp_server.sendto(response.encode(), addr)


def udp_listener():
    print("UDP Voting Server running...")
    while True:
        data, addr = udp_server.recvfrom(BUFFER_SIZE)
        threading.Thread(target=handle_vote, args=(data, addr), daemon=True).start()


# ================= TLS SERVER =================
def handle_tls(client, addr):
    try:
        data = client.recv(BUFFER_SIZE)
        packet = parse_packet(data.decode())

        if packet and packet.get("type") == "get_results":
            response = json.dumps({
                "votes": votes,
                "packet_loss": round(stats.packet_loss(), 2),
                "duplicates": stats.duplicates,
                "invalid_packets": stats.invalid
            })
            client.send(response.encode())
        else:
            client.send(create_error_packet("Invalid control request").encode())

    except Exception as e:
        client.send(create_error_packet(f"Server error: {str(e)}").encode())

    finally:
        client.close()


def tls_server():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain("server.crt", "server.key")

    sock = socket.socket()
    sock.bind((SERVER_BIND_IP, TLS_PORT))
    sock.listen(5)

    print("TLS Control Server running...")

    while True:
        client, addr = sock.accept()
        secure = context.wrap_socket(client, server_side=True)
        threading.Thread(target=handle_tls, args=(secure, addr), daemon=True).start()


# ================= STATS =================
def stats_display():
    while True:
        print("\nVotes:", votes)
    
        print("Loss:", round(stats.packet_loss(), 2), "%")
        print("Duplicates:", stats.duplicates)
        print("Invalid Packets:", stats.invalid)
        time.sleep(BROADCAST_INTERVAL)


# ================= MAIN =================
if __name__ == "__main__":
    threading.Thread(target=udp_listener, daemon=True).start()
    threading.Thread(target=tls_server, daemon=True).start()
    threading.Thread(target=stats_display, daemon=True).start()

    while True:
        time.sleep(1)