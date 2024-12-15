import socket
import threading

BUFFER_SZ = 2048
client_socket = None
client_name = ""
client_status = "Active"
server_ip = "127.0.0.1"
server_port = 6668

def send_message(message):
    try:
        client_socket.send(message.encode())
    except:
        print("Message sending failed.")

def change_status():
    global client_status
    print("\nChoose your status:")
    print("1. Active")
    print("2. Inactive")
    print("3. Busy")
    status_choice = input("Choose your status: ")
    if status_choice == '1':
        client_status = "Active"
    elif status_choice == '2':
        client_status = "Inactive"
    elif status_choice == '3':
        client_status = "Busy"
    else:
        print("Invalid choice, try again.")
        return
    send_message(f"status {client_status}")

def menu():
    while True:
        print("\nMenu:")
        print("1. Talk with all")
        print("2. Direct Message (DM)")
        print("3. Know info of another user by username")
        print("4. Change status (Active/Inactive/Busy)")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            message = input("Enter message to send to all: ")
            send_message(message)
        elif choice == '2':
            recipient_name = input("Enter recipient's username: ")
            dm_message = input(f"Enter message for {recipient_name}: ")
            send_message(f"DM {recipient_name} {dm_message}")
        elif choice == '3':
            username = input("Enter username to get info: ")
            send_message(f"info {username}")
        elif choice == '4':
            change_status()
        elif choice == '5':
            send_message("exit")
            client_socket.close()
            break
        else:
            print("Invalid option, please try again.")

def receive_messages():
    while True:
        try:
            message = client_socket.recv(BUFFER_SZ).decode()
            if message:
                print(message)
        except:
            break

def start_client():
    global client_name
    client_name = input("Enter your name: ")

    client_socket.connect((server_ip, server_port))
    client_socket.send(client_name.encode())  # Send name to server

    threading.Thread(target=receive_messages).start()  # Start receiving messages

    menu()

if __name__ == "__main__":
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    start_client()

