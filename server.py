import socket  # Import socket module
from threading import Thread

# Retain a list of active peers
peer_list = []

# Function needed to break up list of peers
# 1/3 of peers will prompt another 1/3


# handle new peers joining
def client_join(data_list, client_socket):
    host = data_list[1].split(':')[1]
    port = data_list[2].split(':')[1]
    peer_list.append(host + ':' + port)
    print(peer_list)
    client_socket.send('Hello Attendee. Please await instructions...'.encode())


# client exit
def client_exit(data_list, client_socket):
    host = data_list[1].split(':')[1]
    port = data_list[2].split(':')[1]
    print('host {0} at port {1} is quitting'.format(host, port))
    exiting_peer = host + ':' + port
    if exiting_peer in peer_list:
        peer_list.remove(exiting_peer)
        print(peer_list)
    client_socket.send('Bye'.encode())


# handle every bad request from a client
def client_badrequest(data_list, client_socket, data):
    pass


def new_connection(client_socket):
    data = client_socket.recv(1024).decode()
    print('new request from client')
    data_list = data.split('\n')
    for line in data_list:
        print(line)
    if data_list[0].split(' ')[0] == 'JOIN':
        client_join(data_list, client_socket)
    elif data_list[0].split(' ')[0] == 'EXIT':
        client_exit(data_list, client_socket)
    else:
        client_badrequest(data_list, client_socket, data)


# main functionality of the central server
server_socket = socket.socket()  # Create a socket object
# host = socket.gethostname() # Get local machine name
# server_host = socket.gethostbyname(socket.gethostname())
server_host = input('Enter IP address:')
port = 7734  # Reserve a port for your service.
server_socket.bind((server_host, port))  # Bind to the port
print('central server host is ', server_host)
print('central server port is ', port)

server_socket.listen(5)  # Now wait for client connection.
print("Central server is awaiting a connection")
while (True):
    client_socket, client_addr = server_socket.accept()  # Establish connection with client.
    print('Got connection from', client_addr)
    new_thread = Thread(target=new_connection, args=(client_socket,))
    new_thread.start()

# Ask user if they would like to start prompting peers for attendance

print('shutting down central server')
server_socket.close()  # Close the connection
