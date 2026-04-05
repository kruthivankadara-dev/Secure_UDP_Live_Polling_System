import socket
import ssl
import streamlit as st

from config import *
from protocol import *

st.set_page_config(page_title="Live Polling System", page_icon="🗳️", layout="centered")

# ================= SESSION STATE INIT =================
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if "vote" not in st.session_state:
    st.session_state.vote = None

if "clear_flag" not in st.session_state:
    st.session_state.clear_flag = False

# ✅ CLEAR HANDLING BEFORE UI LOAD
if st.session_state.clear_flag:
    st.session_state.user_id = ""
    st.session_state.vote = None
    st.session_state.clear_flag = False

# ================= SEND VOTE =================
def send_vote(user_id: str, vote: str):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(ACK_TIMEOUT)
    server = (SERVER_HOST, UDP_PORT)

    # ✅ Decide packet
    if vote == "INVALID":
        packet = "INVALID_DATA"
    else:
        packet = create_vote_packet(user_id, vote)

    retries = 0
    try:
        while retries < MAX_RETRIES:
            try:
                client.sendto(packet.encode(), server)
                data, _ = client.recvfrom(BUFFER_SIZE)
                response = parse_packet(data.decode())

                if response and response["type"] == "ack":
                    return True, response["message"]
                elif response and "message" in response:
                    return False, response["message"]
                else:
                    return False, "Unknown response from server."
            except socket.timeout:
                retries += 1

        return False, "Server did not respond. Retry limit reached."
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        client.close()

# ================= GET RESULTS =================
def get_secure_results():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    sock = socket.socket()
    secure = context.wrap_socket(sock, server_hostname="localhost")

    try:
        secure.settimeout(5)
        secure.connect((SERVER_HOST, TLS_PORT))
        secure.send(create_results_request().encode())
        data = secure.recv(BUFFER_SIZE)
        return True, data.decode()
    except Exception as e:
        return False, f"Error fetching results: {e}"
    finally:
        try:
            secure.close()
        except:
            pass

# ================= UI =================
st.title("🗳️ Secure Live Polling System")
st.write("Submit your vote through UDP and view secure results through TLS.")

with st.form("vote_form"):
    user_id = st.text_input("Enter User ID", key="user_id")
    vote = st.radio("Choose your vote", ["Python", "Java", "C++"], index=None, key="vote")
    submitted = st.form_submit_button("Submit Vote")

col1, col2 = st.columns(2)

# ================= SUBMIT LOGIC =================
if submitted:
    if not user_id.strip():
        st.warning("Please enter a User ID.")

    elif vote is None:
        # ❌ No vote selected → invalid packet
        ok, message = send_vote(user_id.strip(), "INVALID")

        if ok:
            st.success(message)
        else:
            st.error("Invalid packet (no vote selected)")

    else:
        # ✅ Valid vote
        ok, message = send_vote(user_id.strip(), vote)

        if ok:
            st.success(f"Vote successful: {message}")
        else:
            st.error(message)

# ================= BUTTONS =================
with col1:
    if st.button("Get Secure Results"):
        ok, result = get_secure_results()
        if ok:
            st.subheader("Secure Results")
            st.code(result, language="json")
        else:
            st.error(result)

with col2:
    if st.button("Clear Screen"):
        st.session_state.clear_flag = True
        st.rerun()

# ================= FOOTER =================
st.markdown("---")
st.markdown("### Run")
st.code("python server.py\nstreamlit run streamlit_app.py", language="bash")