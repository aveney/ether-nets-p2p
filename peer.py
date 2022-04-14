import base64
import socket
from threading import Thread
import os
import re
import pickle


class P2P:
    # Dictionary to retain active peers
    activePeers = {}

    eventStarted = False
    eventCoordinator = False
    imageSent = False

    peerID = 0
    sendingPeerID = 0

    serverHost = ""
    serverPort = 0


# This will handle the uploading of images/messages
def peerServer(peerPort):
    # Create socket for peer server
    peerServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerServer.bind((get_ip(), peerPort))
    peerServer.listen(2)
    while (True):
        (clientSocket, clientAddress) = peerServer.accept()
        # print('Got connection from', clientAddress)
        newThread = Thread(target=peerConnection, args=(clientSocket,))
        newThread.start()
    upload_socket.close()


def peerConnection(clientSocket):
    data = clientSocket.recv(2)
    lengthOfMessage = int.from_bytes(data, 'little')
    # print(lengthOfMessage)
    data = clientSocket.recv(lengthOfMessage)
    # print('received ', len(data))
    print('\nNew message:')
    messageContent = data[1:]
    messageType = data[:1]

    # Determine the message type provided by another peer
    print(messageType)
    # print(messageContent)

    if (messageType == b'P'):
        ReceiveImage(messageContent)

    if (messageType == b'L'):
        unpackActivePeers(data)

    if (messageType == b'A'):
        unpackAcknowledgementStatement(data)

    if (messageType == b'M'):
        unpackEventStart(data)

    if (messageType == b'I'):
        unpackPeerId(data)
    # Change status of the event to started
    P2P.eventStarted = True
    clientSocket.close()


# Send Image to the Peer
def sendImage(image, receivingPeerHost, receivingPeerPort):
    # print(image)
    with open(image, "rb") as imageToSend:
        converted_image = base64.b64encode(imageToSend.read())
    # added
    # with open('encode.bin', "wb") as imageToSend:
    #    imageToSend.write(converted_image)
    # print(converted_image)
    # code
    # Encode the message type
    messageType = 'P'.encode()

    # Fill message content
    messageContent = converted_image

    # Append message type to message content
    #       messageType +
    message = messageType + messageContent
    print(message)
    # Get the size of the message
    messageSize = len(message)

    peerID = P2P.peerID

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # print(message)
    # Create socket to send the image
    peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket.connect((receivingPeerHost, receivingPeerPort))

    # print("beforewhile")
    peerSocket.send(message)
    # print("massage:")
    # print(message)

    P2P.imageSent = True


# Decode image from the peer
def ReceiveImage(messageContent):
    print(messageContent)

    decodeit = open('image.jpeg', 'wb')
    decodeit.write(base64.b64decode((messageContent)))
    # print(byte)
    decodeit.close()

    sendAcknowledgementForImage()
    promptImageResponse()


# Send to peer
# def sendToPeer(message):
#     # The name and port number of peers receiving images/messages
#     receivingPeerHost = input("Enter the hostname of the peer:")
#     receivingPeerPort = int(input("Enter port number of the peer:"))
#
#     # Create socket an send message
#     peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     peerSocket.connect((receivingPeerHost, receivingPeerPort))
#     peerSocket.send(message.encode())
#     peerSocket.close()


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
    # print("You have reached sendRequestToServer ")
    print(messageType)

    # Determine the message type provided by server
    if (messageType == b'L'):
        unpackActivePeers(response)
    if (messageType == b'S'):
        unpackAttendanceStatus(response)
    if (messageType == b'M'):
        unpackEventStart(response)
    if (messageType == b'A'):
        unpackAcknowledgementStatement(response)
    clientSocket.close()


# Send the response of the peer responding to the image with message type "U"
def packImageResponse(serverHost, serverPort, response, peerID):
    peerHost = P2P.activePeers[peerID][0]
    peerPort = P2P.activePeers[peerID][1]
    print("Made it to imageResponse")
    messageType = 'U'.encode()

    # peerID hardcoded until P is written

    message = str(peerID) + " " + peerHost + " " + str(peerPort) + " " + response

    message = messageType + message.encode()

    messageSize = len(message)
    message = messageSize.to_bytes(2, 'little') + message
    # print(message)
    # print(message[1:])

    # sending response to index server
    sendRequestToServer(message, serverHost, serverPort)


# Send the dictionary of active peers with message type "L"
def sendActivePeers(peerSocket):
    # print("Sending active peers list...")

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


# Request dictionary of active peers from the index server with message type "R"
def getActivePeers(serverHost, serverPort):
    messageContent = serverHost + " " + str(serverPort) + " " + "GET"

    messageType = 'R'.encode()

    message = messageType + messageContent.encode()

    messageSize = len(message)

    message = messageSize.to_bytes(2, "little") + message

    # replaced note with message
    sendRequestToServer(message, serverHost, serverPort)


# Send request to index server to join network with message type "J"
def joinIndexServer(serverHost, serverPort):
    # Encode the message type
    messageType = 'J'.encode()

    # Fill message content
    messageContent = peerHost + " " + str(peerPort) + " " + "JOIN"

    # Append message type to message content
    message = messageType + messageContent.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send message
    sendRequestToServer(message, serverHost, serverPort)


# Send acknowledge statement to a peer with message type "A"
def peerAcknowledgementStatement(peerSocket):
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
    # sendToPeer(message)
    peerSocket.send(message)
    peerSocket.close()


# Send message to server that event coordinator has started event
def sendEventStartedToServer(serverHost, serverPort):
    # Encode the message type
    messageType = 'M'.encode()

    # Fill message content
    messageContent = "Event started"

    # Append message type to message content
    message = messageType + messageContent.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send message
    sendRequestToServer(message, serverHost, serverPort)


# Sent by event coordinator to let peers know the event has started
def sendEventStartedToPeer(peerSocket):
    # Encode the message type
    messageType = 'M'.encode()

    # Fill message content
    messageContent = "Event started"

    # Append message type to message content
    message = messageType + messageContent.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    # Send message
    peerSocket.send(message)
    peerSocket.close()


def sendPeerId(peerSocket):
    # Encode the message type
    messageType = 'I'.encode()

    # Fill message content
    message = str(P2P.peerID)

    message = messageType + message.encode()

    # Get the size of the message
    messageSize = len(message)

    # Append message size to the message
    message = messageSize.to_bytes(2, 'little') + message

    peerSocket.send(message)
    peerSocket.close()


def unpackPeerId(message):
    messageContent = message[1:]

    P2P.sendingPeerID = int(messageContent.decode())
    print(P2P.sendingPeerID)


# Unpack the message type sending the list of active peers
def unpackActivePeers(message):
    # Message content
    messageContent = message[2:]
    serializedActivePeers = messageContent[1:]

    # Convert the byte string to a dictionary object
    deserializedActivePeers = pickle.loads(serializedActivePeers)

    # Update the current list of active peers
    P2P.activePeers = deserializedActivePeers
    #print(P2P.activePeers)

    if (P2P.eventCoordinator == True):
        print("\nEvent attendees: " + str(len(P2P.activePeers) - 1))
        print("Input 1 to start meeting")
        print("Input option here:")


# unpack attendance status
def unpackAttendanceStatus(message):
    # Message content
    message = message[2:].decode()
    attendance = message[1:]

    # Print attendance status
    print(attendance)


# Unpack acknowledge message type
def unpackAcknowledgementStatement(message):
    # Message content
    messageContent = message[1:]
    unpackedAcknowledgement = messageContent.decode()

    # Print acknowledgement statement
    print(unpackedAcknowledgement)


# Unpack event status message type
def unpackEventStart(message):
    # Change the status of the event for the meeting organizer
    P2P.eventStarted = True

    # Message content
    unpackedStartMessage = message[1:].decode()

    # Print event start confirmation
    print(unpackedStartMessage)

    if P2P.peerID == 0:
        notifyPeers()
    else:
        promptForImageTest()


# Notify peers (meeting attendee) that the event has started
def notifyPeers():
    currentPeer = 1
    while (currentPeer < len(P2P.activePeers)):
        peerHost = P2P.activePeers[currentPeer][0]
        peerPort = P2P.activePeers[currentPeer][1]

        # print(peerHost)
        # print(peerPort)

        currentPeer += 1

        # Socket for sending active peers
        sendPeerActivePeers(peerHost, peerPort)

        # Socket for sending start of event
        sendPeerEventStart(peerHost, peerPort)


def sendPeerEventStart(peerHost, peerPort):
    peerSocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket2.connect((peerHost, int(peerPort)))
    sendEventStartedToPeer(peerSocket2)


def sendPeerActivePeers(peerHost, peerPort):
    peerSocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket1.connect((peerHost, int(peerPort)))
    sendActivePeers(peerSocket1)


# Prompt event attendees to send images to their peers
def promptForImageTest():
    # getActivePeers(serverHost, serverPort)
    # The name and port number of peers receiving images/messages

    if (P2P.peerID == 1):
        image = input("Enter the location of image to be sent to the peer:")
        peerHost1 = P2P.activePeers[2][0]
        peerPort1 = P2P.activePeers[2][1]
        peerHost2 = P2P.activePeers[3][0]
        peerPort2 = P2P.activePeers[3][1]
        sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
    elif (P2P.peerID == 2):
        image = input("Enter the location of image to be sent to the peer:")
        peerHost1 = P2P.activePeers[1][0]
        peerPort1 = P2P.activePeers[1][1]
        peerHost2 = P2P.activePeers[3][0]
        peerPort2 = P2P.activePeers[3][1]
        sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
    elif (P2P.peerID == 3):
        image = input("Enter the location of image to be sent to the peer:")
        peerHost1 = P2P.activePeers[1][0]
        peerPort1 = P2P.activePeers[1][1]
        peerHost2 = P2P.activePeers[2][0]
        peerPort2 = P2P.activePeers[2][1]
        sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)


def sendAcknowledgementForImage():
    peerHost = P2P.activePeers[P2P.sendingPeerID][0]
    peerPort = P2P.activePeers[P2P.sendingPeerID][1]
    peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket.connect((peerHost, int(peerPort)))
    peerAcknowledgementStatement(peerSocket)


# Prompt event attendees to send images to their peers
# def promptForImage():
#     # getActivePeers(serverHost, serverPort)
#     # The name and port number of peers receiving images/messages
#
#     if (P2P.peerID == 1):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[4][0]
#         peerPort1 = P2P.activePeers[4][1]
#         peerHost2 = P2P.activePeers[7][0]
#         peerPort2 = P2P.activePeers[7][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 2):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[5][0]
#         peerPort1 = P2P.activePeers[5][1]
#         peerHost2 = P2P.activePeers[8][0]
#         peerPort2 = P2P.activePeers[8][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 3):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[6][0]
#         peerPort1 = P2P.activePeers[6][1]
#         peerHost2 = P2P.activePeers[9][0]
#         peerPort2 = P2P.activePeers[9][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 4):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[1][0]
#         peerPort1 = P2P.activePeers[1][1]
#         peerHost2 = P2P.activePeers[7][0]
#         peerPort2 = P2P.activePeers[7][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 5):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[2][0]
#         peerPort1 = P2P.activePeers[2][1]
#         peerHost2 = P2P.activePeers[8][0]
#         peerPort2 = P2P.activePeers[8][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 6):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[3][0]
#         peerPort1 = P2P.activePeers[3][1]
#         peerHost2 = P2P.activePeers[9][0]
#         peerPort2 = P2P.activePeers[9][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 7):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[1][0]
#         peerPort1 = P2P.activePeers[1][1]
#         peerHost2 = P2P.activePeers[4][0]
#         peerPort2 = P2P.activePeers[4][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 8):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[2][0]
#         peerPort1 = P2P.activePeers[2][1]
#         peerHost2 = P2P.activePeers[5][0]
#         peerPort2 = P2P.activePeers[5][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)
#     elif (P2P.peerID == 9):
#         image = input("Enter the location of image to be sent to the peer:")
#         peerHost1 = P2P.activePeers[3][0]
#         peerPort1 = P2P.activePeers[3][1]
#         peerHost2 = P2P.activePeers[6][0]
#         peerPort2 = P2P.activePeers[6][1]
#         sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2)

def sendImageToPeers(image, peerHost1, peerPort1, peerHost2, peerPort2):
    # Socket to send the peerID and image
    peerSocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket1.connect((peerHost1, int(peerPort1)))

    # Send the peerID and image
    sendPeerId(peerSocket1)
    sendImage(image, peerHost1, int(peerPort1))

    peerSocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peerSocket2.connect((peerHost2, int(peerPort2)))

    sendPeerId(peerSocket2)
    sendImage(image, peerHost2, int(peerPort2))


def promptImageResponse():
    if (P2P.imageSent == False):
        print("Enter location of image file, then answer the following question:")
        print("Is peer " + str(P2P.sendingPeerID) + " in attendance?(yes/no)")
    else:
        print("Is peer " + str(P2P.sendingPeerID) + " in attendance?")
        print("Enter yes/no: ")
        print("Enter : ")
    answer = input()
    packImageResponse(serverHost, serverPort, answer, P2P.sendingPeerID)


# Handle quitting
# def quitConnection(serverHost, serverPort):
#     note = "EXIT P2P\nHost: " + serverHost + '\n' + "Port: " + str(serverPort)
#     sendRequestToServer(note, serverHost, serverPort)


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


# Main client functionality
if __name__ == '__main__':
    # The IP address and port number for the client
    peerHost = input("Enter an unused hostname:")
    peerPort = int(input("Enter an unused port:"))

    # The IP address and port number for the server
    serverHost = input("Enter the hostname for the Index Server:")
    serverPort = 7734
    P2P.serverHost = serverHost
    P2P.serverPort = serverPort

    # Message sent to join the system
    joinIndexServer(serverHost, serverPort)

    # Get the peer ID
    P2P.peerID = len(P2P.activePeers) - 1
    print("Your peer ID: " + str(P2P.peerID))

    # Provide the status of event coordinator
    if (P2P.peerID == 0):
        P2P.eventCoordinator = True

    if (len(P2P.activePeers) < 2):
        print("You are the event organizer")
        UploadThread = Thread(target=peerServer, args=(peerPort,))
        UploadThread.start()
        print("Input 1 to start meeting")
        control = 0
        while (control != 1):
            control = int(input("Input option here: "))
        # getActivePeers(serverHost, serverPort)
        sendEventStartedToServer(serverHost, serverPort)

    else:
        print("You are the event attendee")
        uploadThread = Thread(target=peerServer, args=(peerPort,))
        # destroy this upload thread on quitting
        print("Wait for next instructions...")
        # uploadThread.daemon = True
        uploadThread.start()

        # Handle input from the client
        # ******************CODE FOR TESTING FUNCTIONS FOR EVENT ATTENDEE************************
        # while (True):
        # print("What do you want to do? Enter number corresponding to an option you choose:")
        # print("1. Send image")
        # # print("2. Request index from server")
        # # print("3. Send index to a peer")
        # # print("4. Start the meeting")
        # print("5. Send id")
        # print("6. Send image response")
        # # # Functionality of centralized server
        # option = int(input())
        # if (option == 1):
        #     promptForImage(serverHost, serverPort)
        # elif (option == 5):
        #     peerHost = input("Enter peer IP Address:")
        #     peerPort = int(input("Enter the port the peer is running on:"))
        #     peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     peerSocket.connect((peerHost, peerPort))
        #     sendPeerId(peerSocket)
        # elif (option == 6):
        #     response = "yes"
        #     id = 1
        #     packImageResponse(serverHost, serverPort, response, id)

        # elif (option == 2):
        #     getActivePeers(serverHost, serverPort)
        # elif (option == 3):
        #     peerHost = input("Enter peer IP Address:")
        #     peerPort = int(input("Enter the port the peer is running on:"))
        #     peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     peerSocket.connect((peerHost, peerPort))
        #     sendActivePeers(peerSocket)
        # elif (option == 4):
        #     sendEventStartedToServer(serverHost, serverPort)
        # else:
        #     print('please enter a valid choice')
