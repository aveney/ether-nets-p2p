import socket
from threading import Thread
import pickle


class P2P:
    # Dictionary to retain active peers
    activePeers = {}

    peerID = 0

    eventStarted = False


# Get attendance status from client and then pack it
def packAttendanceStatus(attendanceStatus, clientSocket):
    # encode the message type
    messageType = 'S'.encode()

    # get attendance status
    attendance = attendanceStatus.encode()

    # append message type to attendance
    message = messageType + attendance

    # get the length of the message
    messageSize = len(message)

    # convert message to bytes
    message = messageSize.to_bytes(2, "little") + message

    clientSocket.send(message)

    clientSocket.close()


# Send active peers dictionary to the requesting client
def provideActivePeers(clientSocket):
    # Get IP and port from client
    # host = messageData[1].split(':')[1]
    # port = messageData[2].split(':')[1]

    print("Sending active peers list...")

    messageType = 'L'.encode()
    # Convert dictionary of active peers to a byte string
    serializedActivePeers = pickle.dumps(P2P.activePeers)
    message = messageType + serializedActivePeers
    messageSize = len(message)

    message = messageSize.to_bytes(2, 'little') + message
    # Send the string
    clientSocket.send(message)
    # clientSocket.close()


def indexAcknowledgeStatement(clientSocket):
    # Sending Acknowledge Statement to Index Server
    # Encode the message type
    messageType = 'A'.encode()

    # Fill message content
    messageContent = 'Message Sent'

    # Append message type to message content
    message = messageType + messageContent.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send message
    clientSocket.send(message)
    clientSocket.close()


def sendEventStarted(clientSocket):
    P2P.eventStarted = True

    # Encode the message type
    messageType = 'M'.encode()

    # Fill message content
    messageContent = "Event confirmed"

    # Append message type to message content
    message = messageType + messageContent.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send message
    clientSocket.send(message)
    clientSocket.close()


# Client joining the network
def unpackJoin(messageData, clientSocket, peerID):
    message = messageData[2:].decode()
    peerInfo = message[1:]
    print(peerInfo)
    # Get IP and port from client
    host = peerInfo.split(' ')[0]
    port = peerInfo.split(' ')[1]

    if (peerID == 0):
        clientInfo = [host, port, "Organizer"]
        P2P.activePeers[peerID] = clientInfo
        print("organizer is : " + str(P2P.activePeers[0]))
        organizerWaitEventStart(clientSocket)
        clientSocket.close()
    else:
        # List for new client information
        clientInfo = [host, port, "Absent", []]
        P2P.activePeers[peerID] = clientInfo
        print("Current Index Server: ")
        print(P2P.activePeers)
        organizerWaitEventStart(clientSocket)
        clientSocket.close()


# Unpacking function for requesting peer dictionary for index server
def unpackRequestActivePeers(message, clientSocket):
    message = message[2:].decode()
    peerInfo = message[1:]
    print(peerInfo)

    print("Current Index Server: ")
    print(P2P.activePeers)
    provideActivePeers(clientSocket)


def unpackImageResponse(messageData):
    # peer Id is hard coded right now
    # waiting for P message type to be done

    print("made it to unpack image response")
    message = messageData[2:].decode()
    peerInfo = message[1:]
    print(message)

    sendingPeerID = int(peerInfo.split(' ')[0])
    peerHost = peerInfo.split(' ')[1]
    peerPort = int(peerInfo.split(' ')[2])
    peerResponse = peerInfo.split(' ')[3]

    print(sendingPeerID)
    print(peerHost)
    print(peerPort)
    print(peerResponse)

    SendingPeer = P2P.activePeers[sendingPeerID]
    SendingPeer[3].append(peerResponse)

    if (len(SendingPeer[3]) >= 2):
        updatePeerAttendance(sendingPeerID, peerHost, peerPort, peerResponse)



    print("updated info is: ")
    print(P2P.activePeers[sendingPeerID])

def updatePeerAttendance (sendingPeerID, peerHost,peerPort,Response):
    yes_count = 0;
    token = False
    for x in P2P.activePeers[sendingPeerID][3]:
        if (x == "token"):
            token = True
        if (x == "no"):
            # Automatically ends for loop if it finds one no
            P2P.activePeers[sendingPeerID][2] = "Absent"
            break;
        elif (x == "yes"):
            yes_count +=1

        if (yes_count >=2):
            #if there are at least 2 yes then they are marked present
            P2P.activePeers[sendingPeerID][2] = "present"
            break;
        if (token == True and yes_count >= 1):
            #passes if one of the peers sends a token and theres one peer the response yes
            P2P.activePeers[sendingPeerID][2] = "present"
            break;

    attendanceStatusToBeSent = P2P.activePeers[sendingPeerID][2]
    newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    newSocket.connect((peerHost, peerPort))
    packAttendanceStatus(attendanceStatusToBeSent, newSocket)




def unpackAcknowledgeStatement(message):
    messageContent = message[2:]
    unpackedAcknowledgement = messageContent[1:]
    print(unpackedAcknowledgement)


def unpackEventStart(message, clientSocket):
    messageContent = message[2:]
    unpackedStartMessage = messageContent[1:].decode()

    # Change status of the event to started
    P2P.eventStarted = True

    # Provide the list of active peers
    provideActivePeers(clientSocket)
    confirmEventStarted()
    print(unpackedStartMessage)


def confirmEventStarted():
    if (len(P2P.activePeers) > 0):
        eventCoordHost = P2P.activePeers[0][0]
        eventCoordPort = P2P.activePeers[0][1]
        peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peerSocket.connect((eventCoordHost, int(eventCoordPort)))
        sendEventStarted(peerSocket)


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
    if (messageType == b'R'):
        unpackRequestActivePeers(message, clientSocket)
    if (messageType == b'U'):
        unpackImageResponse(message)
        indexAcknowledgeStatement(clientSocket)
    if (messageType == b'A'):
        unpackAcknowledgeStatement(message)
    if (messageType == b'M'):
        unpackEventStart(message, clientSocket)
    # print(messageList)

    # for line in messageList:
    #     print(line)
    # if messageList[0].split(' ')[0] == 'J':
    #     clientJoin(messageList, clientSocket, P2P.peerID)
    #     P2P.peerID += 1
    # elif messageList[0].split(' ')[0] == 'R':
    #     provideActivePeers(messageList, clientSocket)


def organizerWaitEventStart(clientSocket):
    # host = clientSocket.split(' ')[0]
    # port = clientSocket.split(' ')[1]              Not used
    # clientInfo = [host, port, "Absent"]
    if (len(P2P.activePeers) == 1):
        provideActivePeers(clientSocket)
    elif (len(P2P.activePeers) > 1):
        provideActivePeers(clientSocket)
        eventCoordHost = P2P.activePeers[0][0]
        eventCoordPort = P2P.activePeers[0][1]
        EventCoordinatorSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        EventCoordinatorSocket.connect((eventCoordHost, int(eventCoordPort)))
        provideActivePeers(EventCoordinatorSocket)


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
