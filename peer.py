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
    print("Peer instructions")
    peerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerServer.bind((get_ip(), peerPort))
    peerServer.listen(2)
    while (True):
        (clientSocket, clientAddress) = peerServer.accept()
        print('Got connection from', clientAddress)
        newThread = Thread(target=peerConnection, args=(clientSocket,))
        newThread.start()
        print("What do you want to do? Enter number corresponding to an option you choose")
        print("1. Send image")
    upload_socket.close()


# Peer connection
def peerConnection(clientSocket):
    data = clientSocket.recv(1034)

    print('New message from peer:')
    messageContent = data[2:]
    messageType = messageContent[:1]

    # Determine the message type provided by another peer
    if (messageType == b'L'):
        unpackActivePeers(data)
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
    clientSocket.send(request)

    # Get the updated dictionary of active peers as a byte string
    response = clientSocket.recv(1024)
    messageContent = response[2:]
    messageType = messageContent[:1]

    # Determine the message type provided by server
    if (messageType == b'L'):
        unpackActivePeers(response)

    clientSocket.close()

# Send the dictionary of active peers with message type "L"
def sendActivePeers(peerSocket):
    print("Sending active peers list...")

    # Encode the message type
    messageType = 'L'.encode()

    # Convert dictionary of active peers to a byte string
    serializedActivePeers = pickle.dumps(P2P.activePeers)

    # Append message type to dictionary strings
    message = messageType + serializedActivePeers

    # Get length of the string
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send the message
    peerSocket.send(message)
    peerSocket.close()


# Unpack the message type sending the list of active peers
def unpackActivePeers(message):
    messageContent = message[2:]
    serializedActivePeers = messageContent[1:]
    # Convert the byte string to a dictionary object
    deserializedActivePeers = pickle.loads(serializedActivePeers)
    P2P.activePeers = deserializedActivePeers
    print(P2P.activePeers)


# Handle quitting
# def quitConnection(serverHost, serverPort):
#     note = "EXIT P2P\nHost: " + serverHost + '\n' + "Port: " + str(serverPort)
#     sendRequestToServer(note, serverHost, serverPort)


# Request dictionary of active peers from the index server
def getActivePeers(serverHost, serverPort):
    note = "R  \nHost: " + serverHost + '\n' + "Port: " + str(serverPort) + "\nGET"
    sendRequestToServer(note, serverHost, serverPort)


# Send request to index server to join network with message type "J"
def joinIndexServer(serverHost, serverPort):
    # Encode the message type
    messageType = 'J'.encode()

    # Fill message content
    messageContent = peerHost + " " + str(peerPort) + " JOIN"

    # Append message type to message content
    message = messageType + messageContent.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send message
    sendRequestToServer(message, serverHost, serverPort)


# Get the IP address from peer machine
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

def sendPeerAcknowledgementStatement():
    # Sending Acknowledge Statement to the peers
    # Encode the message type
    messageType = 'A'.encode()

    # Fill message content
    messageContent = "Image Sent"

    # Append message type to message content
    message = messageType + messageContent.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send message to peer to tell that image was sent
    #sendToPeer(message)
    peerSocket.send(message)
    peerSocket.close()






# Main client functionality
if __name__ == '__main__':
    # The IP address and port number for the client
    peerHost = input("Enter an unused hostname:")
    peerPort = int(input("Enter an unused port:"))

    # The IP address and port number for the server
    serverHost = input("Enter the hostname for the Index Server:")
    serverPort = 7734

    # Message sent to join the system
    joinIndexServer(serverHost, serverPort)

    print("Wait for instructions from event organizer...")
    uploadThread = Thread(target=peerServer, args=(peerPort,))
    # destroy this upload thread on quitting
    uploadThread.daemon = True
    uploadThread.start()

    # Handle input from the client
    while (True):
        print("What do you want to do? Enter number corresponding to an option you choose:")
        print("1. Send image")
        print("2. Request index from server")
        print("3. Send index to a peer")
        # Functionality of centralized server
        option = int(input())
        if (option == 1):
            message = input()
            sendToPeer(message)
        elif (option == 2):
            getActivePeers(serverHost, serverPort)
        elif (option == 3):
            peerHost = input("Enter peer IP Address:")
            peerPort = int(input("Enter the port the peer is running on:"))
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerSocket.connect((peerHost, peerPort))
            sendActivePeers(peerSocket)
        else:
            print('please enter a valid choice')

