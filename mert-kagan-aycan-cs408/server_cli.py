import socket
import threading
import json


class DiSUcordServer:
    def __init__(self, host="0.0.0.0", port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.client_threads = []
        self.connected_clients = (
            {}
        )  # Format: {client_username: (client_socket, client_address)}
        self.channel_subscribers = {"IF100": set(), "SPS101": set()}

    def start(self):
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}", flush=True)
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(
                target=self.handle_client, args=(client_socket,)
            )
            self.client_threads.append(client_thread)
            client_thread.start()

    def handle_client(self, client_socket):
        print(f"New connection", flush=True)
        client_username = self.register_client(client_socket)
        if not client_username:
            return  # Registration failed (likely due to duplicate username)

        # Main loop for client interaction
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if not message:
                    break  # Client probably disconnected

                data = json.loads(message)
                self.process_client_message(client_username, data)

            except socket.timeout:
                print(f"Client {client_username} timed out.", flush=True)
                break
            except Exception as e:
                print(f"Error with client {client_username}: {e}", flush=True)
                break

        # Client disconnected
        self.disconnect_client(client_username, client_socket)

    def register_client(self, client_socket):
        try:
            username_message = client_socket.recv(1024).decode()
            username = json.loads(username_message).get("username")
            if username in self.connected_clients:
                client_socket.send(
                    json.dumps(
                        {"status": "error", "message": "Username already in use"}
                    ).encode()
                )
                client_socket.close()
                return None
            else:
                self.connected_clients[username] = (client_socket, username)
                client_socket.send(
                    json.dumps({"status": "success"}).encode()
                )  # success message to client
                print(
                    f"Client connected successfully: {username}", flush=True
                )  # success message to the server
                return username
        except Exception as e:
            print(f"Error registering client: {e}", flush=True)
            return None

    def process_client_message(self, client_username, data):
        "".lower()
        type = data.get("type").lower()  # to ensure interoperability
        if type == "subscribe":
            self.subscribe_client_to_channel(client_username, data.get("channel"))
        elif type == "unsubscribe":
            self.unsubscribe_client_from_channel(client_username, data.get("channel"))
        elif type == "send":
            self.send_message_to_all(
                client_username, data.get("channel"), data.get("message")
            )

    def subscribe_client_to_channel(self, client_username, channel):
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].add(client_username)
            print(f"Subscription to {channel} by {client_username}", flush=True)

    def unsubscribe_client_from_channel(self, client_username, channel):
        if (
            channel in self.channel_subscribers
            and client_username in self.channel_subscribers[channel]
        ):
            self.channel_subscribers[channel].remove(client_username)
            print(f"Unsubscription from {channel} by {client_username}", flush=True)

    def send_message_to_all(self, sender_username, channel, message):
        if sender_username in self.channel_subscribers.get(channel, set()):
            for subscriber in self.channel_subscribers[channel]:
                if subscriber != sender_username:
                    subscriber_socket = self.connected_clients[subscriber][0]
                    try:
                        subscriber_socket.send(
                            json.dumps(
                                {
                                    "channel": channel,
                                    "message": message,
                                    "from": sender_username,
                                }
                            ).encode()
                        )
                    except:
                        print(f"Error sending message to {subscriber}", flush=True)

            print(f"Message from {sender_username} in {channel}: {message}", flush=True)

    def disconnect_client(self, client_username, client_socket):
        print(f"Client disconnected: {client_username}", flush=True)
        client_socket.close()
        del self.connected_clients[client_username]
        for channel in self.channel_subscribers.values():
            channel.discard(client_username)

    # Function to cleanly shut down the server
    def shutdown(self):
        for client_username, (client_socket, _) in self.connected_clients.items():
            client_socket.close()
        self.server_socket.close()
        for thread in self.client_threads:
            thread.join()
        print("Server shutdown completed.", flush=True)


# Example to start the server
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the DiSUcordServer.")
    parser.add_argument(
        "--port", type=int, default=12345, help="The port number to start the server on."
    )
    args = parser.parse_args()

    server = DiSUcordServer(port=args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        server.shutdown()
