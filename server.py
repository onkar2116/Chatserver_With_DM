import socket
import threading

MAX_CLIENTS = 4
BUFFER_SZ = 2048

class Client:
    def __init__(self, sockfd, address, uid, name, status="Active"):
        self.sockfd = sockfd
        self.address = address
        self.uid = uid
        self.name = name
        self.status = status 

clients = []
clients_mutex = threading.Lock()
uid = 0  
server_ip = "127.0.0.1"  
server_port = 6668

def broadcast(message, sender):
    with clients_mutex:
        for client in clients:
            if client != sender:
                try:
                    client.sockfd.send(message.encode())
                except:
                    print(f"Failed to send message to {client.name}")

def send_direct_message(sender, recipient_name, message):
    with clients_mutex:
        for client in clients:
            if client.name == recipient_name:
                try:
                    client.sockfd.send(f"DM from {sender.name}: {message}".encode())
                    sender.sockfd.send(f"DM to {recipient_name}: {message}".encode())
                    return
                except:
                    print(f"Failed to send DM to {client.name}")
                    return
        sender.sockfd.send(f"User {recipient_name} not found.".encode())

def handle_client(client):
    while True:
        try:
            message = client.sockfd.recv(BUFFER_SZ).decode()
            if message:
                if message == 'exit':
                    broadcast(f"{client.name} has left the chat.", client)
                    with clients_mutex:
                        clients.remove(client)
                    client.sockfd.close()
                    break
                elif message.startswith("status"):
                    _, status = message.split(' ', 1)
                    client.status = status
                    broadcast(f"{client.name} is now {client.status}.", client)
                elif message.startswith("DM"):
                    _, recipient_name, dm_message = message.split(' ', 2)
                    send_direct_message(client, recipient_name, dm_message)
                elif message.startswith("info"):
                    _, target_name = message.split(' ', 1)
                    with clients_mutex:
                        target_client = next((c for c in clients if c.name == target_name), None)
                    if target_client:
                        info_message = f"Username: {target_client.name}, IP: {target_client.address[0]}, Status: {target_client.status}"
                        client.sockfd.send(info_message.encode())
                    else:
                        client.sockfd.send(f"User {target_name} not found.".encode())
                else:
                    broadcast(f"{client.name} ({client.status}): {message}", client)
        except Exception as e:
            print(f"Error handling client {client.name}: {e}")
            break

def accept_connections(server_socket):
    global uid
    while True:
        client_sockfd, client_address = server_socket.accept()
        client_name = client_sockfd.recv(32).decode()  # Receive client name
        new_client = Client(client_sockfd, client_address, uid, client_name)
        with clients_mutex:
            clients.append(new_client)
        print(f"{client_name} has joined the chat.")
        broadcast(f"{client_name} has joined the chat.", new_client)
        threading.Thread(target=handle_client, args=(new_client,)).start()
        uid += 1

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(MAX_CLIENTS)
    print("Server started. Waiting for clients to connect...")
    accept_connections(server_socket)

if __name__ == "__main__":
    start_server()

