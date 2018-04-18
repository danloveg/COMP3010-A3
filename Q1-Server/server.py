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
from subprocess import PIPE, Popen
import traceback
from clientquery import ClientQuery

class HTTPServer:
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


    def __init__(self):
        self.serverSocket = None


    def main(self):
        try:
            os.chdir(self.DOCUMENT_ROOT)
            self.createserversocket()
            self.listentoconnections(socket.SOMAXCONN)
        except KeyboardInterrupt as k:
            print "\nProgram interrupted. Exiting..."
        except Exception as exc:
            traceback.print_exc()
        finally:
            if self.serverSocket:
                self.serverSocket.close()


    def createserversocket(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.HOST, self.ASSIGNED_PORT_NUM))


    def listentoconnections(self, numconnections):
        self.serverSocket.listen(numconnections)
        print "Server is listening for connections on port {0}".format(self.ASSIGNED_PORT_NUM)

        while True:
            self.acceptclientconnections()


    def acceptclientconnections(self):
        clientSocket, clientAddress = self.serverSocket.accept()
        print "Accepted Client: {0}, {1}".format(clientAddress[0], clientSocket.getsockname()[1])

        clientLines = self.receiveclientmessageaslist(clientSocket)

        if self.ishttpmessage(clientLines[0]):
            requestMethod = self.getrequestmethod(clientLines[0])
            fileRequested = self.getrequestedresourcepath(clientLines[0])
            filePath = self.getrelativefilepath(fileRequested)
            parameters = self.geturiparameters(fileRequested)

            query = ClientQuery(clientLines)

            # If directory, try to serve index.html
            if os.path.isdir(filePath):
                filePath += 'index.html' if filePath[-1] == '/' else '/index.html'

            if requestMethod == 'GET' or requestMethod == 'POST':
                if os.path.isfile(filePath):
                    # Execute script if CGI
                    if filePath.find('.cgi') != -1:
                        if requestMethod == 'GET':
                            self.executescript(clientSocket, filePath, parameters, 'GET')
                        else:
                            self.executescript(clientSocket, filePath, clientLines[-1], 'POST')
                    # Otherwise spit the file out to the client
                    else:
                        self.outputfiletoclient(clientSocket, filePath)
                else:
                    # File does not exist. Send 404
                    header = self.createhttpheaders(404, 'Not Found', False, 'text/html')
                    self.respondtoclient(clientSocket, header, self.ERR_PAGE_404, 'GET')
            else:
                header = self.createhttpheaders(501, 'Not Implemented', False, 'text/html')
                self.respondtoclient(clientSocket, header, self.ERR_PAGE_501, 'GET')
        else:
            print "Client sent bad HTTP message. Ignoring."

        if clientSocket:
            clientSocket.close()


    def receiveclientmessageaslist(self, clientsocket):
        message = clientsocket.recv(self.MAX_PACKET_SIZE)
        return message.split('\n')


    def ishttpmessage(self, firstlineofmessage):
        firstlinesplit = firstlineofmessage.split(' ') if firstlineofmessage else []
        return firstlinesplit and len(firstlinesplit) >= 2
    

    def serverequestoclient(self, clientsocket, clientquery):
        if clientquery.isvalidrequestmethod():
            if clientquery.fileexists():
                if clientquery.fileisscript()
                    self.executescript(clientsocket, clientquery)
                else:
                    self.outputfiletoclient(clientsocket, clientquery)
            else:
                header = self.createhttpheaders(404, 'Not Found', False, 'text/html')
                fauxQueryFirstLine = ["GET {} HTTP/1.0".format(self.ERR_PAGE_404)]
                self.respondtoclient(clientSocket, header, ClientQuery(fauxQueryFirstLine))
        else:
            header = self.createhttpheaders(501, 'Not Implemented', False, 'text/html')
            fauxQueryFirstLine = ["GET {} HTTP/1.0".format(self.ERR_PAGE_501)]
            self.respondtoclient(clientSocket, header, ClientQuery(fauxQueryFirstLine))


    def getrequestmethod(self, firstlineofmessage):
        return firstlineofmessage.split(' ')[0]
    

    def getrequestedresourcepath(self, firstlineofmessage):
        return firstlineofmessage.split(' ')[1]


    def getrelativefilepath(self, requestedfilepath):
        if requestedfilepath != '/':
            filePath = requestedfilepath.split('?')[0][1:]
        else:
            filePath = 'index.html'

        return filePath


    def geturiparameters(self, requestedfilepath):
        if requestedfilepath.find('?') != -1:
            parameters = requestedfilepath.split('?')[1]
        else:
            parameters = ""

        return parameters


    def executescript(self, csocket, filepath, parameters, method):
        """
        Executes the script requested by the client.
        """
        self.socketFile = None
        execInformation = {}

        with open(filepath, 'r') as f:
            firstLine = f.readline()

        prog = firstLine[2:] if len(firstLine) > 2 and firstLine[0:3].find('#!') != -1 else None
        prog = prog.replace('\n', '')

        if prog:
            header = self.createhttpheaders(200, 'OK', True)
        else:
            header = self.createhttpheaders(500, 'Internal Server Error', False, 'text/html')
            self.respondtoclient(csocket, header, self.ERR_PAGE_500, 'GET')
            return

        # Set up environment for subprocess
        procEnv = os.environ.copy()
        procEnv['REQUEST_METHOD'] = method
        procEnv['self.SERVER_NAME'] = self.SERVER_NAME
        procEnv['SERVER_PORT'] = str(self.ASSIGNED_PORT_NUM)
        procEnv['self.SERVER_PROTOCOL'] = self.SERVER_PROTOCOL

        execInformation['program'] = prog

        if method == 'GET':
            # Finish setting up environment
            procEnv['QUERY_STRING'] = parameters
            execInformation['environment'] = procEnv
            self.respondtoclient(csocket, header, filepath, method, True, execInformation)
        elif method == 'POST':
            # Finish setting up environment
            procEnv['CONTENT_LENGTH'] = str(len(parameters))
            execInformation['environment'] = procEnv
            # POST requires communicating parameters to subprocess
            execInformation['parameters'] = parameters
            self.respondtoclient(csocket, header, filepath, method, True, execInformation)


    def outputfiletoclient(self, csocket, filepath):
        """
        Creates an appropriate header and uses self.respondtoclient to send the header
        and file to the client. Only txt, html, and js files are allowed.
        """
        fType = filepath.split('.')[-1]
        supported = True if fType in self.SUPPORTED_TYPES else False

        if supported:
            if fType == 'txt' or fType == 'html':
                header = self.createhttpheaders(200, 'OK', False, 'text/html')
            elif fType == 'js':
                header = self.createhttpheaders(200, 'OK', False, 'text/javascript')
        else:
            header = self.createhttpheaders(501, 'Not Implemented', False, 'text/html')
            filePath = self.ERR_PAGE_501

        self.respondtoclient(csocket, header, filepath, 'GET')


    def respondtoclient(self, csocket, header, filepath, method, script=False, execInfo=None):
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
        self.socketFile = None

        try:
            # Get a file handle for the socket and write the header first
            self.socketFile = csocket.makefile('w')

            # If not a script, just output the file
            if not script and method == 'GET':
                self.socketFile.write(header)
                self.socketFile.flush()
                with open(filepath, 'r') as f:
                    for line in f:
                        self.socketFile.write(line)

            # If script and GET, execute w/ params in environment
            elif script and method == 'GET':
                self.socketFile.write(header)
                self.socketFile.flush()
                proc = Popen(
                    [execInfo['program'], filepath],
                    env=execInfo['environment'],
                    stdout=self.socketFile)

            # If script and POST, execute w/ params as stdin
            elif script and method == 'POST':
                self.socketFile.write(header)
                self.socketFile.flush()
                proc = Popen(
                    [execInfo['program'], filepath],
                    env=execInfo['environment'],
                    stdin=PIPE,
                    stdout=self.socketFile)

                # Send parameters
                proc.communicate(input=execInfo['parameters'])

        except:
            traceback.print_exc()
        finally:
            if self.socketFile:
                self.socketFile.close()


    def createhttpheaders(self, status, statusMsg, cgi=False, contentType=None):
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
        messageArray.append('Server:{0}\n'.format(self.SERVER_NAME))

        if not cgi and contentType:
            messageArray.append('Content-Type:{0}\n\n'.format(contentType))

        return ''.join(messageArray)
