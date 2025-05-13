import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import queue
from cryptography.fernet import Fernet
from conf import host, port, fernet_key

class ChatClient:
    def __init__(self, host, port, nickname):
        self.host = host
        self.port = port
        self.nickname = nickname
        self.fernet = Fernet(fernet_key)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = queue.Queue()
        
        try:
            self.client.connect((self.host, self.port))
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't connect: {e}")
            return
        
        self.setup_gui()
        self.receive_thread = threading.Thread(target=self.receive, daemon=True)
        self.receive_thread.start()
        self.root.mainloop()
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(f"Chat - {self.nickname}")
        
        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled')
        self.chat_area.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        self.msg_entry = tk.Entry(self.root)
        self.msg_entry.pack(padx=20, pady=5, fill=tk.X)
        self.msg_entry.bind("<Return>", self.send_message)
        
        self.send_btn = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_btn.pack(padx=20, pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.process_queue)
    
    def process_queue(self):
        while not self.queue.empty():
            msg = self.queue.get()
            self.chat_area.configure(state='normal')
            self.chat_area.insert(tk.END, msg + "\n")
            self.chat_area.configure(state='disabled')
            self.chat_area.see(tk.END)
        self.root.after(100, self.process_queue)
    
    def receive(self):
        while True:
            try:
                message_bytes = self.client.recv(1024)
                if not message_bytes:
                    break
                
                try:
                    decrypted = self.fernet.decrypt(message_bytes).decode('utf-8')
                    self.queue.put(decrypted)
                except:
                    try:
                        message_str = message_bytes.decode('utf-8')
                        if message_str == 'NICK':
                            self.client.send(self.nickname.encode('utf-8'))
                        else:
                            self.queue.put(message_str)
                    except:
                        self.queue.put("[Unknown message]")
            except Exception as e:
                print(f"Error: {e}")
                self.client.close()
                break
    
    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message:
            full_msg = f"{self.nickname}: {message}"
            encrypted = self.fernet.encrypt(full_msg.encode('utf-8'))
            try:
                self.client.send(encrypted)
                self.msg_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Сouldn't send: {e}")
    
    def on_close(self):
        self.client.close()
        self.root.destroy()

if __name__ == "__main__":
    nickname = input("Enter Your nickname: ")
    ChatClient(host, port, nickname)