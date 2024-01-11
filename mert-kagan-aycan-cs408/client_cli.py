import socket
import threading
import json
import sys
 
class DiSUcordClientCLI:
    def __init__(self, server_ip, server_port, username):
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # function to connect to server
    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.send_message({"username": self.username})
            response = self.receive_message()
            if response.get("status") == "error":
                print(f"Connection error: {response.get('message')}", flush=True)
                return False
            print(f"Connected to server as {self.username}", flush=True)
            return True
        except Exception as e:
            print(f"Error connecting to server: {e}", flush=True)
            return False
        
        
    # function to send message to server
    def send_message(self, message):
        try:
            self.client_socket.send(json.dumps(message).encode())
        except OSError:
            print("Disconnected from server.", flush=True)
            sys.exit(1)
        except Exception as e:
            print(f"Error sending message: {e}", flush=True)

    def receive_message(self):
        try:
            message = self.client_socket.recv(1024).decode()
            return json.loads(message)
        except OSError:
            print("Disconnected from server.", flush=True)
            sys.exit(1)
        except Exception as e:
            print(f"Error receiving message: {e}", flush=True)
            return {}

    def handle_command(self, command):
        parts = command.strip().split()
        # we split to get the first word in the command, which is the command itself
        if not parts:
            return

        if parts[0] == "subscribe" and len(parts) == 2:
            self.send_message({"type": "subscribe", "channel": parts[1]})
            print(f"Subscribed to {parts[1]}", flush=True)

        elif parts[0] == "unsubscribe" and len(parts) == 2:
            self.send_message({"type": "unsubscribe", "channel": parts[1]})
            print(f"Unsubscribed from {parts[1]}", flush=True)

        elif parts[0] == "send" and len(parts) >= 3:
            channel = parts[1]
            message = " ".join(parts[2:])
            self.send_message({"type": "send", "channel": channel, "message": message})
            print(f"Message sent to {channel}: {message}", flush=True)

        elif parts[0] == "disconnect":
            self.disconnect()
            sys.exit(0)

    def start_receiving_messages(self):
        while True:
            message = self.receive_message()
            if message:
                print(
                    f"New message in {message['channel']} from {message['from']}: {message['message']}",
                    flush=True,
                )

    def disconnect(self):
        self.client_socket.close()
        print("Disconnected from server.", flush=True)


# Main execution
if __name__ == "__main__":
    print("Enter server IP:", flush=True)
    server_ip = input().strip()
    print("Enter server port:", flush=True)
    server_port = int(input().strip())
    print("Enter your username:", flush=True)
    username = input().strip()

    client = DiSUcordClientCLI(server_ip, server_port, username)
    if client.connect_to_server():
        message_thread = threading.Thread(target=client.start_receiving_messages)
        message_thread.start()

        # Command loop
        try:
            while True:
                command = input()
                client.handle_command(command)
        except KeyboardInterrupt:
            client.disconnect()
