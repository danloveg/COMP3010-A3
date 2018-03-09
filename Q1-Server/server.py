#!/usr/bin/python

"""
 COMP3010 A1 - Q1

 Author: Daniel Lovegrove

 Version: Feb 28/2018

 Purpose: Act as a web server and serve files to a client using only basic
 sockets. No high level objects are allowed (such as ServerSocket). The types of
 requests allowed are GET and POST, a 501 page is sent if another type is sent.
 The server descends into the DOCUMENT_ROOT directory before serving files.
"""

import socket
import os
import subprocess
from subprocess import PIPE, Popen
import traceback

# CONSTANTS
HOST = ''
ASSIGNED_PORT_NUM = 15048 # The socket I was assigned in class
MAX_PACKET_SIZE = 2048
DOCUMENT_ROOT = './site/'
SERVER_NAME = 'python-web-server'
SERVER_PROTOCOL = 'HTTP/1.0'
SUPPORTED_TYPES = ['txt', 'html', 'js']
ERR_PAGE_404 = './errorPages/404page.html'
ERR_PAGE_500 = './errorPages/500page.html'
ERR_PAGE_501 = './errorPages/501page.html'

# GLOBAL VARIABLES
clientSocket = None
socketFile   = None
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


def getPathAndParams(fileRequestedPath):
    """
    Get the file path and any GET parameters from the request path the client
    sent. Returns the path and params in a tuple (<path>, <params>). If the path
    is /, both strings are empty, if there are no parameters, the parameters
    string is empty.
    Parameters:
        - fileRequestedPath: A path of the form <path>?<params>
    Returns:
        - The full path, and any parameters after the '?' in a string
    """
    filePath = ""
    parameters = ""

    if fileRequestedPath != '/':
        if fileRequestedPath.find('?') != -1:
            filePath, parameters = fileRequestedPath.split('?')
            filePath = filePath[1:]
        else:
            filePath = fileRequestedPath
            filePath = filePath[1:]
    else:
        filePath = 'index.html'

    return (filePath, parameters)


def executeScript(csocket, filepath, parameters, method):
    """
    Executes the script requested by the client.
    """
    socketFile = None
    execInformation = {}

    with open(filepath, 'r') as f:
        firstLine = f.readline()

    prog = firstLine[2:] if len(firstLine) > 2 and firstLine[0:3].find('#!') != -1 else None
    prog = prog.replace('\n', '')

    if prog:
        header = createHttpHeaders(200, 'OK', True)
    else:
        header = createHttpHeaders(500, 'Internal Server Error', False, 'text/html')
        respondToClient(csocket, header, ERR_PAGE_500, 'GET')
        return

    # Set up environment for subprocess
    procEnv = os.environ.copy()
    procEnv['REQUEST_METHOD'] = method
    procEnv['SERVER_NAME'] = SERVER_NAME
    procEnv['SERVER_NAME'] = str(ASSIGNED_PORT_NUM)
    procEnv['SERVER_PROTOCOL'] = SERVER_PROTOCOL

    execInformation['program'] = prog

    if method == 'GET':
        # Finish setting up environment
        procEnv['QUERY_STRING'] = parameters
        execInformation['environment'] = procEnv
        respondToClient(csocket, header, filepath, method, True, execInformation)
    elif method == 'POST':
        # Finish setting up environment
        procEnv['CONTENT_LENGTH'] = str(len(parameters))
        execInformation['environment'] = procEnv
        # POST requires communicating parameters to subprocess
        execInformation['parameters'] = parameters
        respondToClient(csocket, header, filepath, method, True, execInformation)


def outputFileToClient(csocket, filepath):
    """
    Creates an appropriate header and uses respondToClient to send the header
    and file to the client. Only txt, html, and js files are allowed.
    """
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

    respondToClient(csocket, header, filepath, 'GET')


def respondToClient(csocket, header, filepath, method, script=False, execInfo=None):
    """
    Send the header and contents of a file to the client or execute a script and
    pipe the output of it to the client.
    Parameters:
    - csocket: The socket the client is connected to
    - header: The header to write to the client
    - filepath: The path of the file to send or execute
    - script: True if executing script at filepath, else False
    - execInfo: Contains environment and script interpreter in a dictionary.
      (eg., execInfo['program']='/usr/bin/perl', execInfo['environment']=os.environ.copy())
    """
    socketFile = None

    try:
        # Get a file handle for the socket and write the header first
        socketFile = csocket.makefile('w')

        # If not a script, just output the file
        if not script and method == 'GET':
            socketFile.write(header)
            socketFile.flush()
            with open(filepath, 'r') as f:
                for line in f:
                    socketFile.write(line)

        # If script and GET, execute w/ params in environment
        elif script and method == 'GET':
            socketFile.write(header)
            socketFile.flush()
            proc = Popen(
                [execInfo['program'], filePath],
                env=execInfo['environment'],
                stdout=socketFile)

        # If script and POST, execute w/ params as stdin
        elif script and method == 'POST':
            socketFile.write(header)
            socketFile.flush()
            proc = Popen(
                [execInfo['program'], filePath],
                env=execInfo['environment'],
                stdin=PIPE,
                stdout=socketFile)

            # Send parameters
            proc.communicate(input=execInfo['parameters'])

    except:
        traceback.print_exc()
    finally:
        if socketFile: socketFile.close()


def createHttpHeaders(status, statusMsg, cgi=False, contentType=None):
    """
    Creates HTTP header with a status code and message. If the header is for a 
    CGI script, only the first line is included. If the header is not for a CGI
    script but a regular file, the first line, Content-Type, and the blank line
    is included.
    Parameters:
        - status: Integer HTTP status code (eg., 200)
        - statusMsg: Message to go along with status (eg., OK)
        - cgi: Set to true if header is for a CGI script
        - contentType: Type of content header is for (eg., text/html)
    Returns:
        String containing the HTTP header
    """
    messageArray = []
    messageArray.append('HTTP/1.0 {code} {msg}\n'.format(code=status, msg=statusMsg))
    messageArray.append('Server:{0}\n'.format(SERVER_NAME))

    if not cgi and contentType:
        # CGI script is responsible for generating this.
        messageArray.append('Content-Type:{0}\n\n'.format(contentType))

    return ''.join(messageArray)


# ------------------------------------------------------------------------------
# Start of Processing
# ------------------------------------------------------------------------------

try:
    # Descend into document root
    os.chdir(DOCUMENT_ROOT)
    # Create server socket, listen and accept connections
    address = (HOST, ASSIGNED_PORT_NUM)
    serverSocket = startServer(address, socket.SOMAXCONN)

    while True:
        clientSocket, clientAddress = serverSocket.accept()
        print "Accepted Client: {0}, {1}".format(clientAddress[0], clientSocket.getsockname()[1])

        # Receive data from Client
        clientMessage = clientSocket.recv(MAX_PACKET_SIZE)

        # Process Client message
        clientLines = clientMessage.split('\n')
        firstLine = clientLines[0].split(' ') if clientLines[0] else []

        if firstLine and firstLine[0] and firstLine[1]:
            requestMethod, fileRequested = (clientLines[0].split(' '))[0:2]
            (filePath, parameters) = getPathAndParams(fileRequested)

            # If directory, try to server index.html
            if os.path.isdir(filePath):
                filePath += 'index.html' if filePath[-1] == '/' else '/index.html'

            if requestMethod == 'GET' or requestMethod == 'POST':
                if (os.path.isfile(filePath)):
                    # Execute script if CGI
                    if filePath.find('.cgi') != -1:
                        if requestMethod == 'GET':
                            executeScript(clientSocket, filePath, parameters, 'GET')
                        else:
                            executeScript(clientSocket, filePath, clientLines[-1], 'POST')
                    # Otherwise spit the file out to the client
                    else:
                        outputFileToClient(clientSocket, filePath)
                else:
                    # File does not exist. Send 404
                    header = createHttpHeaders(404, 'Not Found', False, 'text/html')
                    respondToClient(clientSocket, header, ERR_PAGE_404, 'GET')
            else:
                header = createHttpHeaders(501, 'Not Implemented', False, 'text/html')
                respondToClient(clientSocket, header, ERR_PAGE_501, 'GET')

        # Close client socket when done
        if clientSocket: clientSocket.close()

except KeyboardInterrupt as k:
    print "\nProgram interrupted. Exiting..."

except Exception as e:
    traceback.print_exc()

finally:
    if clientSocket: clientSocket.close()
    if serverSocket: serverSocket.close()

