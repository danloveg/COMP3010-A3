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
import const

class HTTPServer:
    ERR_PAGE_404 = './errorPages/404page.html'
    ERR_PAGE_500 = './errorPages/500page.html'
    ERR_PAGE_501 = './errorPages/501page.html'


    def __init__(self):
        self.serverSocket = None


    def main(self):
        try:
            os.chdir(const.DOCUMENT_ROOT)
            self.createserversocket()
            self.listentoconnections(socket.SOMAXCONN)
        except KeyboardInterrupt:
            print "\nProgram interrupted. Exiting..."
        except Exception:
            traceback.print_exc()
        finally:
            if self.serverSocket:
                self.serverSocket.close()


    def createserversocket(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind(('', const.ASSIGNED_PORT_NUM))


    def listentoconnections(self, numconnections):
        self.serverSocket.listen(numconnections)
        print "Server is listening for connections on port {0}".format(const.ASSIGNED_PORT_NUM)

        while True:
            self.acceptclientconnections()


    def acceptclientconnections(self):
        clientSocket, clientAddress = self.serverSocket.accept()
        print "Accepted Client: {0}".format(clientAddress[0])

        clientLines = self.receiveclientmessageaslist(clientSocket)

        if self.ishttpmessage(clientLines[0]):
            query = ClientQuery(clientLines)
            self.serverequestoclient(clientSocket, query)
        else:
            print "Client sent bad HTTP message. Ignoring."

        if clientSocket:
            clientSocket.close()


    def receiveclientmessageaslist(self, clientsocket):
        message = clientsocket.recv(const.MAX_PACKET_SIZE)
        return message.split('\n')


    def ishttpmessage(self, firstlineofmessage):
        firstlinesplit = firstlineofmessage.split(' ') if firstlineofmessage else []
        return firstlinesplit and len(firstlinesplit) >= 2
    

    def serverequestoclient(self, clientsocket, clientquery):
        if clientquery.isvalidrequestmethod():
            if clientquery.fileexists():
                self.respondtoclient(clientsocket, clientquery)
            else:
                self.senderrorpage(clientsocket, 404)
        else:
            self.senderrorpage(clientsocket, 501)


    def respondtoclient(self, clientsocket, clientquery):
        fileType = clientquery.getfiletype()

        if fileType == 'cgi':
            header = self.createscripthttpheader(200, 'OK')
        elif fileType == 'js':
            header = self.createfilehttpheader(200, 'OK', 'application/javascript')
        elif fileType == 'txt' or fileType == 'html':
            header = self.createfilehttpheader(200, 'OK', 'text/html')
        else:
            self.senderrorpage(clientsocket, 501)
            return

        clientquery.setheader(header)

        socketFile = None
        try:
            socketFile = csocket.makefile('w')
            socketFile.write(header)
            socketFile.flush()

            if fileType != 'cgi':
                self.sendfiletoclient(socketFile, clientquery)
            elif clientquery.getrequestmethod() == 'GET':
                self.executescriptget(socketFile, clientquery)
            elif clientquery.getrequestmethod() == 'POST':
                self.executescriptpost(socketFile, clientquery)
            else:
                self.senderrorpage(clientsocket, 501)

        except:
            traceback.print_exc()
        finally:
            if socketFile:
                socketFile.close()


    def sendfiletoclient(self, clientsocketfile, clientquery):
        with open(clientquery.getfilepath(), 'r') as f:
            for line in f:
                clientsocketfile.write(line)


    def executescriptget(self, clientsocketfile, clientquery):
        proc = Popen(
            [clientquery.getexecutingprogram(), clientquery.getfilepath()],
            env=clientquery.getenvironment(),
            stdout=clientsocketfile)


    def executescriptpost(self, clientsocketfile, clientquery):
        proc = Popen(
            [clientquery.getexecutingprogram(), clientquery.getfilepath()],
            env=clientquery.getenvironment(),
            stdin=PIPE,
            stdout=clientsocketfile)

        proc.communicate(input=clientquery.getparamters())


    def createfilehttpheader(self, status, statusmessage, contenttype):
        messageArray = []
        messageArray.append('HTTP/1.0 {} {}\n'.format(status, statusmessage))
        messageArray.append('Content-Type:{}\n').format(contenttype)
        messageArray.append('Server:{}\n\n'.format(const.SERVER_NAME))
        return ''.join(messageArray)


    def createscripthttpheader(self, status, statusmessage):
        messageArray = []
        messageArray.append('HTTP/1.0 {} {}\n'.format(status, statusmessage))
        messageArray.append('Server:{}\n'.format(const.SERVER_NAME))
        return ''.join(messageArray)


    def senderrorpage(self, clientsocket, errorcode):
        if errorcode == 404:
            header = self.createfilehttpheader(404, 'Not Found', 'text/html')
            fauxQueryFirstLine = ["GET {} HTTP/1.0".format(self.ERR_PAGE_404)]
        elif errorcode == 501:
            header = self.createfilehttpheader(501, 'Not Implemented', 'text/html')
            fauxQueryFirstLine = ["GET {} HTTP/1.0".format(self.ERR_PAGE_501)]
        else:
            header = self.createfilehttpheader(500, 'Internal Server Error', 'text/html')
            fauxQueryFirstLine = ["GET {} HTTP/1.0".format(self.ERR_PAGE_500)]

        newquery = ClientQuery(fauxQueryFirstLine, header)
        self.respondtoclient(clientsocket, newquery)
