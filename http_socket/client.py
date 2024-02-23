import socket
from threading import Thread

client_socket = socket.socket()
port = 9911
host = "127.0.0.1"
client_socket.connect((host, port))

# receive connection message from server
receive_message = client_socket.recv(1024).decode("utf-8")
print("----\n", receive_message, "\n----")

# send user details to the server
send_msg = input("Enter your username with prefix '#' --->>  ")
client_socket.send(send_msg.encode("utf-8"))


def receive_data():
    while True:
        receive_message = client_socket.recv(1024).decode("utf-8")
        print(f"\n{receive_message}\n")


def send_data():
    while True:
        send_message = input("\nSend Your message in format [@user:message] --->>  ")
        if send_message == "bye":
            client_socket.close()
        else:
            client_socket.send(send_message.encode("utf-8"))


# receive and send messages from/to different users
try:
    receive_thread = Thread(target=receive_data)
    receive_thread.start()
    send_thread = Thread(target=send_data)
    send_thread.start()
except Exception as e:
    print(f"--------\n\n{e}\n\n--------")
    client_socket.close()
