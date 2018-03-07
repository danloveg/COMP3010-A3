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
import traceback

HOST = ''
ASSIGNED_PORT_NUM = 15048 # The socket I was assigned in class
MAX_PACKET_SIZE = 2048
SUPPORTED_TYPES = ['txt', 'html', 'js']
clientSocket = None
socketFile   = None
serverSocket = None
ERR_PAGE_404 = './errorPages/404page.html'
ERR_PAGE_500 = './errorPages/500page.html'
ERR_PAGE_501 = './errorPages/501page.html'


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


def getPathAndGETParams(fileRequestedPath):
    """
    Get the file path and any GET parameters from the request path the client
    sent. Returns the path and params in a tuple (<path>, <params>). If the path
    is /, both strings are empty, if there are no parameters, the parameters
    string is empty.
    Parameters:
        - fileRequestedPath: A path of the form <path>?<params>
    Returns:
        - The full path (./<path>), and any parameters after the '?' in a dict
    """
    filePath = ""
    parameters = {}

    if fileRequestedPath != '/':
        if fileRequestedPath.find('?') != -1:
            filePath, paramString = fileRequestedPath.split('?')
            if paramString:
                for keyvalue in paramString.split('&'):
                    (key, val) = keyvalue.split('=')
                    parameters[key] = val
        else:
            filePath = fileRequestedPath

        filePath = '.' + filePath

    return (filePath, parameters)


def executeScript(csocket, filepath, parameters):
    """
    Executes the script requested by the client's GET request.
    """
    socketFile = None

    with open(filepath, 'r') as f:
        firstLine = f.readline()

    prog = firstLine[2:] if len(firstLine) > 2 and firstLine[0:3].find('#!') != -1 else None
    prog = prog.replace('\n', '')

    if prog:
        header = createHttpHeaders(200, 'OK', True)
    else:
        header = createHttpHeaders(500, 'Internal Server Error', False, 'text/html')
        sendHeaderAndFile(csocket, header, ERR_PAGE_500)
        return

    # Create environment
    procEnv = os.environ.copy()
    for param in parameters:
        procEnv[param] = parameters[param]

    # Respond to client
    try:
        socketFile = csocket.makefile('w')
        socketFile.write(header)
        proc = subprocess.Popen([prog, filePath], env=procEnv, stdout=socketFile)
    except Exception:
        traceback.print_exc()
    finally:
        if socketFile: socketFile.close()


def outputFileToClient(csocket, filepath):
    """
    Creates an appropriate header and uses sendHeaderAndFile to send the header
    and file to the client. Only txt and html files are allowed.
    """
    supported = False
    socketFile = None

    fType = filepath.split('.')[-1]
    supported = True if fType in SUPPORTED_TYPES else False

    if supported:
        if fType == 'txt' or fType == 'html':
            header = createHttpHeaders(200, 'OK', False, 'text/html')
        elif fType == 'js':
            header = createHttpHeaders(200, 'OK', False, 'text/javascript')
    else:
        header = createHttpHeaders(501, 'Not Implemented', False, 'text/html')
        filePath = ERR_PAGE_501

    # Respond to client
    sendHeaderAndFile(csocket, header, filepath)


def sendHeaderAndFile(csocket, header, filepath):
    """
    Send the header and contents of file to the client connected on the socket
    """
    socketFile = None

    try:
        socketFile = csocket.makefile('w')
        socketFile.write(header)
        with open(filepath, 'r') as f:
            for line in f:
                socketFile.write(line)
    except Exception:
        traceback.print_exc()
    finally:
        if socketFile: socketFile.close()


def createHttpHeaders(status, statusMsg, cgi=False, contentType=None):
    """
    Creates HTTP header ... (FINISH)
    Parameters:
        - status: Integer HTTP status code
        - output: String output to send to the client
    Returns:
        String containing the HTTP header
    """
    messageArray = []
    messageArray.append('HTTP/1.0 {code} {msg}\n'.format(code=status, msg=statusMsg))

    if not cgi and contentType:
        messageArray.append('Content-Type:{0}\n'.format(contentType))
        messageArray.append('\n')

    return ''.join(messageArray)


# ------------------------------------------------------------------------------
# Start of Processing
# ------------------------------------------------------------------------------

try:
    # Create server socket, listen and accept connections
    address = (HOST, ASSIGNED_PORT_NUM)
    serverSocket = startServer(address, socket.SOMAXCONN)

    while True:
        clientSocket, clientAddress = serverSocket.accept()

        print "\nAccepted the client connection:"
        print "Address: {0}".format(clientAddress[0])
        print "   Port: {0}\n".format(clientSocket.getsockname()[1])

        # Receive data from Client
        clientMessage = getClientMessage(clientSocket)
        clientLines = clientMessage.split('\n')
        requestMethod = (clientLines[0].split(' '))[0]

        if requestMethod == "GET":
            fileRequested = (clientLines[0].split(' '))[1]
            (filePath, parameters) = getPathAndGETParams(fileRequested)

            if (os.path.exists(filePath)):
                # Execute script if CGI
                if filePath.find('.cgi') != -1:
                    executeScript(clientSocket, filePath, parameters)
                # Otherwise spit the file out to the client
                else:
                    outputFileToClient(clientSocket, filePath)
            else:
                # File does not exist. Send 404
                header = createHttpHeaders(404, 'Not Found', False, 'text/html')
                sendHeaderAndFile(clientSocket, header, ERR_PAGE_404)

        elif requestMethod == "POST":
            # Not supported (yet)
            print clientMessage

        else:
            # Unsupported.
            pass

        # Close client socket when done
        if clientSocket: clientSocket.close()

except KeyboardInterrupt as k:
    print "\nProgram interrupted. Exiting..."

except Exception as e:
    traceback.print_exc()

finally:
    if clientSocket: clientSocket.close()
    if serverSocket: serverSocket.close()

