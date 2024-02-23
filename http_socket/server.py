import select
import socket
from uuid import uuid4


def start_server():
    port = 9911
    socket_list = []
    users_connection_data = {}

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port))
    server_socket.listen(5)

    socket_list.append(server_socket)

    while True:
        import time

        time.sleep(2)
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)
        for sock in ready_to_read:
            if sock == server_socket:
                connection, address = server_socket.accept()
                socket_list.append(connection)
                connection_id = str(uuid4())
                socket_object = {connection_id: ["", connection, address]}
                users_connection_data.update(socket_object)
                connection.send(
                    f"You are connected from: {str(address)} as connection_id {connection_id}".encode(
                        "utf-8"
                    )
                )

            else:
                try:
                    data = str(sock.recv(1024).decode("utf-8")).strip()
                    current_connection = sock
                    if data.startswith("#"):
                        current_address = None
                        current_user = (
                            data.strip().replace("#", "").replace(" ", "_").lower()
                        )
                        for value in users_connection_data.values():
                            if value[1] == current_connection:
                                value[0] = current_user
                                current_address = value[2]

                        print(f"User added to list: {current_user}, {current_address}")
                        current_connection.send(
                            f"Your user detail has been saved as {current_user}".encode(
                                "utf-8"
                            )
                        )
                    elif data.startswith("@"):
                        req_user = data[1 : data.index(":")]
                        req_msg = data[data.index(":") + 1 :] or ""
                        print(req_user, "@user-----")
                        print(req_msg, "@msg-----")
                        for value in users_connection_data.values():
                            if value[1] == current_connection:
                                current_user = value[0]
                            if value[0] == req_user:
                                req_connection = value[1]
                        print(req_connection)
                        req_connection.send(
                            f"{current_user.upper()}: {req_msg}".encode("utf-8")
                        )
                        sock.send(
                            f"Successfully sent message to {req_user}".encode("utf-8")
                        )

                except Exception as e:
                    raise e

    server_socket.close()


if __name__ == "__main__":
    start_server()
