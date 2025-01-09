import socket
import threading
import time

SERVER_IP = "localhost"
SERVER_PORT = 12345


def udp_hole_punch(client_socket, peer_public):
    peer_public_ip, peer_public_port = peer_public.split(':')

    print("Starting hole punching...")
    for _ in range(5):
        client_socket.sendto(b"DUMMY_PACKET", (peer_public_ip, int(peer_public_port)))
        time.sleep(1)

    print("Hole punching complete. Waiting for peer response...")
    return True


def send_keep_alive(client_socket, peer_addr):
    while True:
        client_socket.sendto(b"KEEP_ALIVE", peer_addr)
        time.sleep(10)


def listen_for_messages(client_socket):
    while True:
        data, addr = client_socket.recvfrom(1024)
        message = data.decode()

        if message == "CHAT_TERMINATED":
            print("Peer has terminated the chat.")
            client_socket.sendto("ACK_TERMINATION".encode(), (SERVER_IP, SERVER_PORT))
            break

        elif message.startswith("PEER"):
            peer_public = message.split(' ')[1]
            print(f"Received peer details. Public: {peer_public}")
            if udp_hole_punch(client_socket, peer_public):
                peer_addr = (peer_public.split(':')[0], int(peer_public.split(':')[1]))
                threading.Thread(target=send_keep_alive, args=(client_socket, peer_addr), daemon=True).start()
                print("Connection established. Keep-alive started.")

        else:
            print(f"Received: {message}")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    username = input("Enter your username: ")
    client_socket.sendto(f"REGISTER {username}".encode(), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print(response.decode())

    threading.Thread(target=listen_for_messages, args=(client_socket,)).start()

    while True:
        command = input("Enter command (LIST/CONNECT <username>/TERMINATE): ")
        client_socket.sendto(command.encode(), (SERVER_IP, SERVER_PORT))


if __name__ == "__main__":
    main()
