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
address = (HOST, ASSIGNED_PORT_NUM)
clientSocket = None
serverSocket = None


# ------------------------------------------------------------------------------
# Function definitions
# ------------------------------------------------------------------------------

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
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(address)
    serverSocket.listen(socket.SOMAXCONN)
    print "Server is listening for connections on port {0}".format(ASSIGNED_PORT_NUM)
    clientSocket, clientAddress = serverSocket.accept()

    # Receive data from Client
    clientMessage = getClientMessage(clientSocket)
    print clientMessage

except KeyboardInterrupt as k:
    print "\nProgram interrupted. Exiting..."

except Exception as e:
    print "Error: {0}".format(e)

finally:
    if clientSocket:
        clientSocket.close()
    if serverSocket:
       serverSocket.close()

