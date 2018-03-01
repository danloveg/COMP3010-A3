#!/usr/bin/python

"""
 COMP3010 A1 - Q1

 Author: Daniel Lovegrove

 Version: Feb 28/2018

 Purpose: Act as a web server and serve files to a client using only basic
 sockets. No high level objects are allowed (such as ServerSocket).
"""

import socket

HOST = ''
ASSIGNED_PORT_NUM = 15048
MAX_PACKET_SIZE = 512
clientSocket = None
serverSocket = None


# ------------------------------------------------------------------------------
# Function definitions
# ------------------------------------------------------------------------------

def startServer(addr, numConnections):
    """
    Create a server socket for the specified address and return the socket
    Parameters:
        - addr: Host address and port number in a list (<address>, <port>)
        - numConnections: The max number of connections to allow
    """
    ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ssocket.bind(address)
    ssocket.listen(numConnections)
    print "Server is listening for connections on port {0}".format(addr[1])
    return ssocket


def getClientMessage(clientsocket):
    """
    Get the client's message from its socket, and return a string containing it
    Parameters:
        - clientsocket: The socket the client is connected to
    """
    clientMessage = "\0"
    clientMessageArray = []

    # Wait for newline character
    while clientMessage[-1] != '\n':
        clientMessage = clientsocket.recv(MAX_PACKET_SIZE)
        clientMessageArray.append(clientMessage)

    return ''.join(clientMessageArray)


# ------------------------------------------------------------------------------
# Start of Processing
# ------------------------------------------------------------------------------

try:
    # Create server socket, listen and accept connections
    address = (HOST, ASSIGNED_PORT_NUM)
    serverSocket = startServer(address, socket.SOMAXCONN)
    clientSocket, clientAddress = serverSocket.accept()

    print "\nAccepted the client connection:"
    print "Address: {0}".format(clientAddress[0])
    print "   Port: {0}\n".format(clientSocket.getsockname()[1])

    # Receive data from Client
    clientMessage = getClientMessage(clientSocket)
    clientLines = clientMessage.split('\n')
    requestMethod, requestFile = (clientLines[0].split(' '))[0:2]

    print "Client sent {req} request".format(req=requestMethod)
    print "Client wants file: {f}".format(f=requestFile)
    print "Exiting..."

except KeyboardInterrupt as k:
    print "\nProgram interrupted. Exiting..."

except Exception as e:
    print "Error: {0}".format(e)

finally:
    if clientSocket:
        clientSocket.close()
    if serverSocket:
       serverSocket.close()

