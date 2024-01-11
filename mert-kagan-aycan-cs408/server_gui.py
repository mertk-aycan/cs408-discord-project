import tkinter as tk
from subprocess import Popen, PIPE, STDOUT
import threading


class DiSUcordServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("DiSUcord Server")

        # Port Entry
        tk.Label(master, text="Port:").grid(row=0, column=0)
        self.port_entry = tk.Entry(master)
        self.port_entry.grid(row=0, column=1)
        self.port_entry.insert(0, "12345")  # Default port

        # Start and Stop Buttons
        self.start_button = tk.Button(
            master, text="Start Server", command=self.start_server
        )
        self.start_button.grid(row=1, column=0)

        self.stop_button = tk.Button(
            master, text="Stop Server", command=self.stop_server, state=tk.DISABLED
        )
        self.stop_button.grid(row=1, column=1)

        # Output Area
        self.output_text = tk.Text(master, height=20, width=60)
        self.output_text.grid(row=2, column=0, columnspan=2)

        # Server Process
        self.server_process = None

        # Set the function to be called when the window is closed
        self.master.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Client List
        tk.Label(master, text="Client List:").grid(row=3, column=0)
        self.client_list_text = tk.Text(master, height=10, width=30)
        self.client_list_text.grid(row=4, column=0)

        # IF100 Subscriber List
        tk.Label(master, text="IF100 Subscriber List:").grid(row=3, column=1)
        self.if100_subscriber_list_text = tk.Text(master, height=10, width=30)
        self.if100_subscriber_list_text.grid(row=4, column=1)

        # SPS101 Subscriber List
        tk.Label(master, text="SPS101 Subscriber List:").grid(row=5, column=0)
        self.sps101_subscriber_list_text = tk.Text(master, height=10, width=30)
        self.sps101_subscriber_list_text.grid(row=6, column=0)

    def start_server(self):
        port = self.port_entry.get()
        self.server_process = Popen(
            ["python", "server_cli.py", "--port", port],
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
        )
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL

        # Start thread to read output
        threading.Thread(target=self.read_output, daemon=True).start()

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            self.start_button["state"] = tk.NORMAL
            self.stop_button["state"] = tk.DISABLED

            # show it in the UI
            self.output_text.insert(tk.END, "Server stopped\n")
            self.output_text.see(tk.END)

    def delete_if_exists(self, text_widget, username):
        start_index = text_widget.search(username + "\n", "1.0", tk.END)
        if start_index:  # If the username is found in the list
            # calculate stop index
            stop_index = start_index + f"+{len(username)}c"
            # delete username from the list
            text_widget.delete(start_index, stop_index)

    def add_if_not_exists(self, text_widget, username):
        if not text_widget.search(
            username + "\n", "1.0", tk.END
        ):  # If the username is not found in the list
            # add username to the list
            text_widget.insert(tk.END, username + "\n")
            text_widget.see(tk.END)

    def read_output(self):
        while True:
            print("reading line")
            output = self.server_process.stdout.readline()
            print("output is: " + output)
            if output == "" and self.server_process.poll() is not None:
                print("Breaking")
                break
            if output:
                self.output_text.insert(tk.END, output)
                self.output_text.see(tk.END)
            if output.startswith("Client connected successfully:"):
                # get username
                username = output.split(":")[1].strip()
                # add username to client list
                self.add_if_not_exists(self.client_list_text, username)
            if output.startswith("Client disconnected:"):
                # get username
                username = output.split(":")[1].strip()
                # delete if exists in clients
                self.delete_if_exists(self.client_list_text, username)
                # delete if exists in IF100 subscribers
                self.delete_if_exists(self.if100_subscriber_list_text, username)
                # delete if exists in SPS101 subscribers
                self.delete_if_exists(self.sps101_subscriber_list_text, username)

            if output.startswith("Subscription to"):
                # get channel
                channel = output.split(" ")[2].strip()
                # get username
                username = output.split(" ")[4].strip()
                # update list of the channel
                if channel == "IF100":
                    self.add_if_not_exists(self.if100_subscriber_list_text, username)
                elif channel == "SPS101":
                    self.add_if_not_exists(self.sps101_subscriber_list_text, username)
            if output.startswith("Unsubscription from"):
                # get channel
                channel = output.split(" ")[2].strip()
                # get username
                username = output.split(" ")[4].strip()
                # update list of the channel
                if channel == "IF100":
                    # delete if exists
                    self.delete_if_exists(self.if100_subscriber_list_text, username)
                elif channel == "SPS101":
                    # delete if exists
                    self.delete_if_exists(self.sps101_subscriber_list_text, username)

    def on_window_close(self):
        # If the server process is running, terminate it
        if self.server_process:
            self.server_process.terminate()

        # Destroy the window
        self.master.destroy()


# Create and run the GUI application
root = tk.Tk()
app = DiSUcordServerGUI(root)
root.mainloop()
