import socket
from threading import Thread
import os
import re
import pickle


class P2P:
    # Dictionary to retain active peers
    activePeers = {}


# This will handle the uploading of images/messages
def peerServer(peerPort):
    # Create socket for peer server
    peerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerServer.bind((get_ip(), peerPort))
    peerServer.listen(2)
    while (True):
        (clientSocket, clientAddress) = peerServer.accept()
        print('Got connection from', clientAddress)
        newThread = Thread(target=peerConnection, args=(clientSocket,))
        newThread.start()
        newThread.join()
        print("What do you want to do? Enter number corresponding to an option you choose")
        print("1. Send image")
    upload_socket.close()


# Peer connection
def peerConnection(clientSocket):
    data = clientSocket.recv(1034).decode()
    print('New message from peer:')
    print(data)
    clientSocket.close()


# Send to peer
def sendToPeer(message):
    # The name and port number of peers receiving images/messages
    receivingPeerHost = input("Enter the hostname of the peer:")
    receivingPeerPort = int(input("Enter port number of the peer:"))

    # Create socket an send message
    peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket.connect((receivingPeerHost, receivingPeerPort))
    peerSocket.send(message.encode())
    peerSocket.close()


# Send requests to the central server
def sendRequestToServer(request, serverHost, serverPort):
    # Create socket and send message
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverHost, serverPort))
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024)

    # Get the updated dictionary of active peers as a byte string
    # Convert the byte string to a dictionary object
    deserializedActivePeers = pickle.loads(response)
    P2P.activePeers = deserializedActivePeers
    print('Response from the central server:')
    print(P2P.activePeers)
    clientSocket.close()


# Handle quitting
def quitConnection(serverHost, serverPort):
    note = "EXIT P2P\nHost: " + serverHost + '\n' + "Port: " + str(serverPort)
    sendRequestToServer(note, serverHost, serverPort)


# Request dictionary of active peers from the index server
def getActivePeers(serverHost, serverPort):
    note = "GET P2P\nHost: " + serverHost + '\n' + "Port: " + str(serverPort)
    sendRequestToServer(note, serverHost, serverPort)


def get_ip(ifaces=['en0']):
    if isinstance(ifaces, str):
        ifaces = [ifaces]
    for iface in list(ifaces):
        search_str = f'ifconfig {iface}'
        result = os.popen(search_str).read()
        com = re.compile(r'(?<=inet )(.*)(?= netmask)', re.M)
        ipv4 = re.search(com, result)
        if ipv4:
            ipv4 = ipv4.groups()[0]
            return ipv4
    return ''


# Main client functionality
# The IP address and port number for the client
peerHost = input("Enter an unused hostname:")
peerPort = int(input("Enter an unused port:"))

# The IP address and port number for the server
serverHost = input("Enter the hostname for the Index Server:")
serverPort = 7734

# Message sent to join the system
request = "JOIN P2P\nHost: " + peerHost + '\n' + "Port: " + str(peerPort)
sendRequestToServer(request, serverHost, serverPort)

uploadThread = Thread(target=peerServer, args=(peerPort,))
# destroy this upload thread on quitting
uploadThread.daemon = True
uploadThread.start()

# Handle input from the client
while (True):
    print("What do you want to do? Enter number corresponding to an option you choose:")
    print("1. Send image")
    print("2. Request index from server")
    # Functionality of centralized server
    option = int(input())
    if (option == 1):
        message = input()
        sendToPeer(message)
    elif (option == 2):
        getActivePeers(serverHost, serverPort)
    else:
        print('please enter a valid choice')
