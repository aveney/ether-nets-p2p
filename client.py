import socket  # Import socket module
from threading import *
import os
import glob
import sys
import platform
import datetime

quit_flag = False

# THIS METHOD IS CURRENTLY PRESENT TO KEEP PROGRAM RUNNING
# to listen to any peers requiring uploads
def upload_server():
    upload_socket = socket.socket()
    upload_host = socket.gethostbyname(socket.gethostname())
    upload_port = port
    upload_socket.bind((upload_host, upload_port))
    upload_socket.listen(3)
    peer_thread = current_thread()
    while (quit_flag != True):
        (client_socket, client_addr) = upload_socket.accept()
        print('Got connection from', client_addr)
        new_thread = Thread(target=peer_connection, args=(client_socket,))
        new_thread.start()
        new_thread.join()
        print("What do you want to do?Enter number corresponding to an option you choose")
        print("1. Add RFC's")
        print("5. Quit")
    upload_socket.close()


# THIS METHOD IS CURRENTLY PRESENT TO KEEP PROGRAM RUNNING
# peer connection
def peer_connection(client_socket):
    data = client_socket.recv(1024).decode()
    print('new request from peer')
    data_list = data.split('\n')
    for line in data_list:
        print(line)
    rfc = data_list[0].split(' ')[2]
    file_name = "rfc" + str(rfc) + '.txt'
    file_list = glob.glob('*.txt')
    if file_name in file_list:
        # mtime = os.path.getmtime(file_name)
        # last_modified_date = datetime.datetime.fromtimestamp(mtime)
        f_size = os.path.getsize(file_name)
        response = "P2P-CI/1.0 200 OK\n" + "Date: " + str(datetime.datetime.now().strftime(
            "%A, %d. %B %Y %I:%M%p")) + '\nOS: ' + platform.system() + '\n' + 'Content-Length: ' + str(
            f_size) + '\n' + 'Content-Type: text/text'
        client_socket.send(response.encode())
        with open(file_name, 'r') as f:
            file_data = f.read(1024).encode()
            client_socket.send(file_data)
            while file_data != "":
                file_data = f.read(1024).encode()
                client_socket.send(file_data)
    else:
        response = "P2P-CI/1.0 404 Not Found"
        client_socket.send(response.encode())
    client_socket.close()
    print("What do you want to do?Enter number corresponding to an option you choose")
    print("1. Add RFC's")
    print("5. Quit")


# to send requests to the central server_host
def send_requests(note, server_host, server_port):
    client_socket = socket.socket()
    client_socket.connect((server_host, server_port))
    client_socket.send(note.encode())
    response = client_socket.recv(1024).decode()
    print('response from the central server :')
    print(response)
    client_socket.close()


# handle quitting
def quit(server_host, server_port):
    note = "EXIT P2P-CI/1.0\nHost: " + host + '\n' + "Port: " + str(port)
    send_requests(note, server_host, server_port)
    quit_flag = True


# to handle any user input
def handle_input():
    server_host = input("enter the host of the central server: ")
    server_port = 7734
    # for the first time a peer joins the system
    note = "JOIN P2P-CI/1.0\nHost: " + host + '\n' + "Port: " + str(port)
    send_requests(note, server_host, server_port)
    file_list = glob.glob('*.txt')
    # for file in file_list:
    #     title = file.split('.')[0]
    #     rfc = int(title.split('c')[1])
    #     note = "ADD RFC " + str(rfc) + " P2P-CI/1.0\nHost: " + host + '\n' + "Port: " + str(
    #         port) + '\n' + "Title: " + title
    #     send_requests(note, server_host, server_port)
    # after the client joins sucessfully give functionality options
    while (True):
        print("What do you want to do?Enter number corresponding to an option you choose")
        print("5. Quit")
        option = int(input())
        if (option == 5):
            quit(server_host, server_port)
            break
        else:
            print('please enter a valid choice')


# main client functionality
host = input("please enter an unused host name: ")
port = int(input("please enter an unused port number: "))
upload_thread = Thread(target=upload_server)
# destroy this upload thread on quitting
upload_thread.daemon = True
upload_thread.start()

# now handle user input
handle_input()
