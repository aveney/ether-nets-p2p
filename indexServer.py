import socket
from threading import Thread
import pickle


class P2P:
    # Dictionary to retain active peers
    activePeers = {}

    peerID = 0


# Client joining the network
def unpackJoin(messageData, clientSocket, peerID):
    message = messageData[2:].decode()
    peerInfo = message[1:]
    print(peerInfo)
    # Get IP and port from client
    host = peerInfo.split(' ')[0]
    port = peerInfo.split(' ')[1]

    # List for new client information
    clientInfo = [host, port, "Absent"]
    P2P.activePeers[peerID] = clientInfo
    print("Current Index Server: ")
    print(P2P.activePeers)
    provideActivePeers(clientSocket)


# Send active peers dictionary to the requesting client
def provideActivePeers(clientSocket):
    # Get IP and port from client
    #host = messageData[1].split(':')[1]
    #port = messageData[2].split(':')[1]

    print("Sending active peers list...")

    messageType = 'L'.encode()
    # Convert dictionary of active peers to a byte string
    serializedActivePeers = pickle.dumps(P2P.activePeers)
    message = messageType + serializedActivePeers
    messageSize = len(message)

    message = messageSize.to_bytes(2, 'little') + message
    # Send the string
    clientSocket.send(message)
    clientSocket.close()


# Handle new requests from clients
def newConnection(clientSocket):
    # Received a message from the client
    message = clientSocket.recv(1024)
    print("New request from client")
    messageContent = message[2:]
    messageType = messageContent[:1]
    # Determine the type of message received from the client
    if (messageType == b'J'):
        unpackJoin(message, clientSocket, P2P.peerID)
        P2P.peerID += 1
    # print(messageList)

    # for line in messageList:
    #     print(line)
    # if messageList[0].split(' ')[0] == 'J':
    #     clientJoin(messageList, clientSocket, P2P.peerID)
    #     P2P.peerID += 1
    # elif messageList[0].split(' ')[0] == 'R':
    #     provideActivePeers(messageList, clientSocket)


# Functionality of centralized server
if __name__ == '__main__':
    # Create a new socket object
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set the IP address and port for the central server
    serverHost = input("Enter the IP address of the central server: ")
    serverPort = 7734

    # Bind to the port
    serverSocket.bind((serverHost, serverPort))

    # Wait for connection
    serverSocket.listen(5)
    print("Index Server is running...")
    while (True):
        # Establish connection with client
        clientSocket, clientAddress = serverSocket.accept()

        print('Got connection from', clientAddress)
        newThread = Thread(target=newConnection, args=(clientSocket,))
        newThread.start()
    print('shutting down central server')
    serverSocket.close()
