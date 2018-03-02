#!/usr/bin/python

"""
 COMP3010 A1 - Q1

 Author: Daniel Lovegrove

 Version: Feb 28/2018

 Purpose: Act as a web server and serve files to a client using only basic
 sockets. No high level objects are allowed (such as ServerSocket).
"""

import socket
import os
import subprocess

HOST = ''
ASSIGNED_PORT_NUM = 15048 # The socket I was assigned in class
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


def getPathAndGETParams(fileRequestPath):
    """
    Get the file path and any GET parameters from the request path the client
    sent. Returns the path and params in a tuple (<path>, <params>). If the path
    is /, both strings are empty, if there are no parameters, the parameters
    string is empty.
    Parameters:
        - fileRequestPath: A path of the form <path>?<params>
    Returns:
        - The full path (./<path>), and any parameters after the '?' in a dict
    """
    filePath = ""
    parameters = {}

    if fileRequestPath != '/':
        if fileRequestPath.find('?') != -1:
            filePath, paramString = fileRequest.split('?')
            if paramString:
                for keyvalue in paramString.split('&'):
                    (key, val) = keyvalue.split('=')
                    parameters[key] = val
        else:
            filePath = fileRequest
        filePath = '.' + filePath

    return (filePath, parameters)


def createHttpMessageWithHeaders(status, statusMsg, output):
    """
    Creates HTTP header ... (FINISH)
    Parameters:
        - status: Integer HTTP status code
        - output: String output to send to the client
    """
    messageArray = []
    messageArray.append("HTTP/1.0 {code} {msg}".format(code=status, msg=statusMsg)
    return ''.join(messageArray)


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
    requestMethod = (clientLines[0].split(' '))[0]
    print "Client sent {req} request".format(req=requestMethod)

    if requestMethod == "GET":
        fileRequest = (clientLines[0].split(' '))[1]
        (filePath, parameters) = getPathAndGETParams(fileRequest)

        if (os.path.exists(filePath)):
            # Execute script if CGI
            if filePath.find('.cgi') != -1:

                with open(filePath, 'r') as f:
                    fileData = f.readlines()

                execution = fileData[0];

                if (len(execution) < 2 or execution[0:3].find('#!') == -1):
                    print "Script is not executable"
                else:
                    prog = execution[2:].replace('\n', '')
                    # Execute the program
                    procEnv = os.environ.copy()
                    # --- Modify environment --- procEnv['VAR'] = var
                    proc = subprocess.Popen([prog, filePath], env=procEnv)

            # Otherwise spit the file out to the client
            else:
                print "{0} is a regular file.".format(fileRequest)
        else:
            # Serve 404 page
            print "404: file {0} does not exist.".format(filePath)

    elif requestMethod == "POST":
        # Not supported (yet)
        print clientMessage

    else:
        # Unsupported.
        pass

except KeyboardInterrupt as k:
    print "\nProgram interrupted. Exiting..."

except Exception as e:
    print "Error: {0}".format(e)

finally:
    if clientSocket:
        clientSocket.close()
    if serverSocket:
       serverSocket.close()

