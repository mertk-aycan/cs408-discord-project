import tkinter as tk
from subprocess import Popen, PIPE, STDOUT
import threading


class DiSUcordClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("DiSUcord Client")

        # Server IP, Port, Username
        tk.Label(master, text="Server IP:").grid(row=0, column=0)
        self.server_ip_entry = tk.Entry(master)
        self.server_ip_entry.grid(row=0, column=1)

        tk.Label(master, text="Port:").grid(row=1, column=0)
        self.server_port_entry = tk.Entry(master)
        self.server_port_entry.grid(row=1, column=1)

        tk.Label(master, text="Username:").grid(row=2, column=0)
        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=2, column=1)

        self.connect_button = tk.Button(
            master, text="Connect", command=self.connect_to_server
        )
        self.connect_button.grid(row=3, column=0, columnspan=2)

        # Command Input
        self.command_entry = tk.Entry(master)
        self.command_entry.grid(row=4, column=0, columnspan=2)
        self.send_button = tk.Button(
            master, text="Send Command", command=self.send_command
        )
        self.send_button.grid(row=5, column=0, columnspan=2)

        # Output Area
        self.output_text = tk.Text(master, height=10, width=50)
        self.output_text.grid(row=6, column=0, columnspan=2)

        # Disconnect Button
        self.disconnect_button = tk.Button(
            master, text="Disconnect", command=self.disconnect
        )
        self.disconnect_button.grid(row=7, column=0, columnspan=2)

        # IF100 Subscribe/Unsubscribe Buttons
        self.if100_subscribe_button = tk.Button(
            master, text="Subscribe IF100", command=self.subscribe_if100
        )
        self.if100_subscribe_button.grid(row=8, column=0)

        self.if100_unsubscribe_button = tk.Button(
            master, text="Unsubscribe IF100", command=self.unsubscribe_if100
        )
        self.if100_unsubscribe_button.grid(row=8, column=1)

        # SPS101 Subscribe/Unsubscribe Buttons
        self.sps101_subscribe_button = tk.Button(
            master, text="Subscribe SPS101", command=self.subscribe_sps101
        )
        self.sps101_subscribe_button.grid(row=9, column=0)

        self.sps101_unsubscribe_button = tk.Button(
            master, text="Unsubscribe SPS101", command=self.unsubscribe_sps101
        )
        self.sps101_unsubscribe_button.grid(row=9, column=1)

        # Channel Message
        self.channel_var = tk.StringVar()

        tk.Label(master, text="Channel:").grid(row=10, column=0)
        tk.Radiobutton(
            master, text="IF100", variable=self.channel_var, value="IF100"
        ).grid(row=10, column=1)
        tk.Radiobutton(
            master, text="SPS101", variable=self.channel_var, value="SPS101"
        ).grid(row=10, column=2)

        tk.Label(master, text="Message:").grid(row=11, column=0)
        self.message_entry = tk.Entry(master)
        self.message_entry.grid(row=11, column=1)

        self.send_message_button = tk.Button(
            master, text="Send Message", command=self.send_message
        )
        self.send_message_button.grid(row=12, column=0, columnspan=2)

        # CLI Process
        self.cli_process = None
        
        # Set the function to be called when the window is closed
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)
        


    def connect_to_server(self):
        server_ip = self.server_ip_entry.get()
        server_port = self.server_port_entry.get()
        username = self.username_entry.get()

        self.cli_process = Popen(
            ["python", "client_cli.py"],
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
        )

        # Sending server details to CLI
        self.cli_process.stdin.write(server_ip + "\n")
        self.cli_process.stdin.write(server_port + "\n")
        self.cli_process.stdin.write(username + "\n")
        self.cli_process.stdin.flush()

        # Start thread to read output
        threading.Thread(target=self.read_output, daemon=True).start()

    def send_command(self):
        command = self.command_entry.get()
        self.cli_process.stdin.write(command + "\n")
        self.cli_process.stdin.flush()
        self.command_entry.delete(0, tk.END)

    def read_output(self):
        while True:
            output = self.cli_process.stdout.readline()
            if output == "" and self.cli_process.poll() is not None:
                break
            if output:
                self.output_text.insert(tk.END, output)
                self.output_text.see(tk.END)

    def disconnect(self):
        if self.cli_process:
            self.cli_process.stdin.write("disconnect\n")
            self.cli_process.stdin.flush()
            self.cli_process.terminate()

    def subscribe_if100(self):
        self.cli_process.stdin.write("subscribe IF100\n")
        self.cli_process.stdin.flush()

    def unsubscribe_if100(self):
        self.cli_process.stdin.write("unsubscribe IF100\n")
        self.cli_process.stdin.flush()

    def subscribe_sps101(self):
        self.cli_process.stdin.write("subscribe SPS101\n")
        self.cli_process.stdin.flush()

    def unsubscribe_sps101(self):
        self.cli_process.stdin.write("unsubscribe SPS101\n")
        self.cli_process.stdin.flush()

    def send_message(self):
        channel = self.channel_var.get()  # Use get method of StringVar
        message = self.message_entry.get()
        self.cli_process.stdin.write(f"send {channel} {message}\n")
        self.cli_process.stdin.flush()
        self.message_entry.delete(0, tk.END)

    def on_window_close(self):
        # If the server process is running, terminate it
        if self.cli_process:
            self.cli_process.terminate()

        # Destroy the window
        self.master.destroy()

# Create and run the GUI application
root = tk.Tk()
app = DiSUcordClientGUI(root)
root.mainloop()
