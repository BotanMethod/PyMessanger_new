import socket
import threading
from conf import host, port
from time import strftime

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f'Connected {str(address)}')

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"User's nickname: {nickname}")
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'))
        client.send("You're connected to the server!".encode('utf-8'))

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

print('Server launched!')
print(f'Launch time: {strftime("%Y-%m-%d %H:%M:%S")}')
receive()