def create_vote_packet(user_id, vote):
    return f"VOTE|{user_id}|{vote}"


def create_ack_packet(message):
    return f"ACK|{message}"


def create_error_packet(message):
    return f"ERROR|{message}"


def create_results_request():
    return "GET_RESULTS"


def parse_packet(packet):
    try:
        parts = packet.strip().split("|")

        if parts[0] == "VOTE" and len(parts) == 3:
            return {"type": "vote", "user": parts[1], "vote": parts[2]}

        elif parts[0] == "ACK":
            return {"type": "ack", "message": "|".join(parts[1:])}

        elif parts[0] == "ERROR":
            return {"type": "error", "message": "|".join(parts[1:])}

        elif parts[0] == "GET_RESULTS":
            return {"type": "get_results"}

        return None
    except:
        return None