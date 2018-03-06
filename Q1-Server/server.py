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
clientFile   = None
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


def executeScript(csocket, filepath, parameters):
    """
    Comments.
    """
    executable = True

    with open(filepath, 'r') as f:
        fileData = f.readlines()

    execution = fileData[0];

    # Determine if executable
    if (execution and len(execution) < 2 or execution[0:3].find('#!') == -1):
        executable = False

    if executable:
        # Set up the execution of the program
        prog = execution[2:].replace('\n', '')

        # Create environment
        procEnv = os.environ.copy()
        for param in parameters:
            procEnv[param] = parameters[param]

        # Create OK header
        header = createHttpHeaders(200, 'OK', True)

    else:
        # Create Internal Server Error header
        header = createHttpHeaders(500, 'Internal Server Error', False, 'text/html')

    # Create a file to pipe stdout from script to
    socketFile = csocket.makefile('w')

    if socketFile:
        try:
            socketFile.write(header)
            if executable:
                proc = subprocess.Popen([prog, filePath], env=procEnv, stdout=socketFile)
            else:
                socketFile.write('<!DOCTYPE html>\n<body>')
                socketFile.write('<h1>500 Internal Server Error</h1>')
                socketFile.write('<p>The script requested is not executable.</p>')
                socketFile.write('</body>\n</html>')

        except Exception as e:
            print 'Error: {0}'.format(e)
        finally:
            socketFile.close()
    else:
        print 'Could not make client file.'


def outputFileToClient(csocket, filepath):
    notImpl = False
    fileLines = []

    fType = filepath.split('.')[-1]

    if fType == 'txt' or fType == 'html':
        # File is OK, read it
        with open(filepath, 'r') as f:
            fileLines = f.readlines()

        # Create OK header
        header = createHttpHeaders(200, 'OK', False, 'text/html')
    else:
        # Create Not Implemented header
        header = createHttpHeaders(501, 'Not Implemented', False, 'text/html')
        # header = 'HTTP/1.0 501 Not Implemented\nContent-Type:text/html\n\n'
        notImpl = True

    # Get socket file handle
    clientFile = csocket.makefile('w')

    if clientFile:
        try:
            # Send appropriate header
            clientFile.write(header)

            # Send file
            if notImpl == False:
                for line in fileLines:
                    clientFile.write(line)

            # Otherwise send 501 message.
            else:
                clientFile.write('<!DOCTYPE html>\n<body>')
                clientFile.write('<h1>501 Not Implemented</h1>')
                clientFile.write('<p>This file type is not supported.</p>')
                clientFile.write('</body>\n</html>')

        except Exception as e:
            print 'Error: {0}'.format(e)
        finally:
            clientFile.close()


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
            fileRequest = (clientLines[0].split(' '))[1]
            (filePath, parameters) = getPathAndGETParams(fileRequest)

            if (os.path.exists(filePath)):
                # Execute script if CGI
                if filePath.find('.cgi') != -1:
                    executeScript(clientSocket, filePath, parameters)

                # Otherwise spit the file out to the client
                else:
                    outputFileToClient(clientSocket, filePath)
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

