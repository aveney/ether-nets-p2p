import socket
from threading import Thread
import pickle


class P2P:
    # Dictionary to retain active peers
    activePeers = {}

    peerID = 0


# Client joining the network
def clientJoin(dataList, clientSocket, peerID):
    # Get IP and port from client
    host = dataList[1].split(':')[1]
    port = dataList[2].split(':')[1]

    # List for new client information
    clientInfo = [host, port, "Absent"]
    P2P.activePeers[peerID] = clientInfo
    print("Current Index Server: ")
    print(P2P.activePeers)

    # Convert dictionary of active peers to a byte string
    serializedActivePeers = pickle.dumps(P2P.activePeers)
    # Send the string
    clientSocket.send(serializedActivePeers)
    clientSocket.close()


# Send active peers dictionary to the requesting client
def provideList(dataList, clientSocket):
    # Get IP and port from client
    host = dataList[1].split(':')[1]
    port = dataList[2].split(':')[1]

    print("Sending active peers list...")

    # Convert dictionary of active peers to a byte string
    serializedActivePeers = pickle.dumps(P2P.activePeers)
    # Send the string
    clientSocket.send(serializedActivePeers)
    clientSocket.close()


# Handle new requests from clients
def newConnection(clientSocket):
    # Received a message from the client
    message = clientSocket.recv(1024).decode()
    print("New request from client")
    messageList = message.split('\n')
    # print(messageList)
    # Determine the type of message received from the client
    for line in messageList:
        print(line)
    if messageList[0].split(' ')[0] == 'J':
        clientJoin(messageList, clientSocket, P2P.peerID)
        P2P.peerID += 1
    elif messageList[0].split(' ')[0] == 'R':
        provideList(messageList, clientSocket)


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
