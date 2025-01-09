import socket
import threading

STUN_SERVER_IP = "localhost"
STUN_SERVER_PORT = 12345

clients = {}  # Store clients with username as key


def register_client(addr, username, server_socket):
    if username in clients:
        server_socket.sendto("ERROR Username already taken.".encode(), addr)
        return

    clients[username] = {
        "public_endpoint": addr,
        "status": "available",
        "peer": None,
    }

    print(f"Registered {username} at {addr}")
    server_socket.sendto("REGISTERED".encode(), addr)


def list_clients(addr, server_socket):
    available_clients = [
        user for user, details in clients.items() if details["status"] == "available"
    ]
    response = "AVAILABLE_CLIENTS " + ",".join(available_clients)
    server_socket.sendto(response.encode(), addr)


def send_peer_details(requester, target_username, server_socket):
    requester_details = clients[requester]
    target_details = clients[target_username]

    requester_public = f"{requester_details['public_endpoint'][0]}:{requester_details['public_endpoint'][1]}"
    target_public = f"{target_details['public_endpoint'][0]}:{target_details['public_endpoint'][1]}"

    # Inform both clients
    server_socket.sendto(f"PEER {target_public}".encode(), requester_details["public_endpoint"])
    server_socket.sendto(f"PEER {requester_public}".encode(), target_details["public_endpoint"])

    # Update statuses
    requester_details["status"] = "busy"
    requester_details["peer"] = target_username
    target_details["status"] = "busy"
    target_details["peer"] = requester


def connect_clients(addr, target_username, server_socket):
    requester = next((user for user, details in clients.items() if details["public_endpoint"] == addr), None)

    if not requester:
        server_socket.sendto("ERROR You are not registered.".encode(), addr)
        return

    if target_username not in clients:
        server_socket.sendto("ERROR Target client not found.".encode(), addr)
        return

    target_details = clients[target_username]

    # Check if target is already busy
    if target_details["status"] != "available":
        server_socket.sendto("ERROR Target client is busy.".encode(), addr)
        return

    # Notify target client about the request
    server_socket.sendto(f"REQUEST {requester}".encode(), target_details["public_endpoint"])


def terminate_chat(addr, server_socket):
    requester = next((user for user, details in clients.items() if details["public_endpoint"] == addr), None)

    if not requester:
        server_socket.sendto("ERROR You are not registered.".encode(), addr)
        return

    if clients[requester]["status"] != "busy":
        server_socket.sendto("ERROR You are not in a chat.".encode(), addr)
        return

    peer = clients[requester]["peer"]

    # Inform the peer about termination
    peer_details = clients[peer]
    server_socket.sendto("CHAT_TERMINATED".encode(), peer_details["public_endpoint"])

    # Wait for acknowledgment
    ack_data, _ = server_socket.recvfrom(1024)
    if ack_data.decode() == "ACK_TERMINATION":
        clients[requester]["status"] = "available"
        clients[peer]["status"] = "available"
        server_socket.sendto("CHAT_TERMINATED".encode(), addr)
    else:
        server_socket.sendto("ERROR Termination acknowledgment failed.".encode(), addr)


def handle_client(data, addr, server_socket):
    request = data.decode().split(' ', 1)
    command = request[0]

    if command == "REGISTER":
        username = request[1]
        register_client(addr, username, server_socket)
    elif command == "LIST":
        list_clients(addr, server_socket)
    elif command == "CONNECT":
        target_username = request[1]
        connect_clients(addr, target_username, server_socket)
    elif command == "TERMINATE":
        terminate_chat(addr, server_socket)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((STUN_SERVER_IP, STUN_SERVER_PORT))

    print(f"STUN Server listening on {STUN_SERVER_IP}:{STUN_SERVER_PORT}")

    while True:
        data, addr = server_socket.recvfrom(1024)
        client_handler = threading.Thread(target=handle_client, args=(data, addr, server_socket))
        client_handler.start()


if __name__ == "__main__":
    main()
