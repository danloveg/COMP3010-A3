#!/usr/bin/python

import os
import const

class ClientQuery:
    def __init__(self, clientmessageaslist, header=None):
        self._requestMethod = self._determinerequestmethod(clientmessageaslist[0])
        fileRequested = self._determinerequestedresourcepath(clientmessageaslist[0])
        self._filePath = self._determinerelativefilepath(fileRequested)
        self._program = self._determineexecutingprogram(clientmessageaslist)

        if self._requestMethod == 'GET':
            self._parameters = self._determineuriparameters(fileRequested)
        elif self._requestMethod == 'POST':
            self._parameters = clientmessageaslist[-1]

        if header != None:
            self._header = header

        self._setupenvironment()


    def _setupenvironment(self):
        self._environment = os.environ.copy()
        self._environment['REQUEST_METHOD'] = self._requestMethod
        self._environment['SERVER_NAME'] = const.SERVER_NAME
        self._environment['SERVER_PORT'] = str(const.ASSIGNED_PORT_NUM)
        self._environment['SERVER_PROTOCOL'] = const.SERVER_PROTOCOL
        if self._requestMethod == 'GET':
            self._environment['QUERY_STRING'] = self._parameters
        elif self._requestMethod == 'POST':
            self._environment['CONTENT_LENGTH'] = str(len(self._parameters))


    def _determinerequestmethod(self, firstlineofmessage):
        return firstlineofmessage.split(' ')[0]
    

    def _determinerequestedresourcepath(self, firstlineofmessage):
        return firstlineofmessage.split(' ')[1]


    def _determinerelativefilepath(self, requestedfilepath):
        if requestedfilepath != '/':
            filePath = requestedfilepath.split('?')[0][1:]
        else:
            filePath = 'index.html'

        if os.path.isdir(filePath):
            filePath += 'index.html' if filePath[-1] == '/' else '/index.html'

        return filePath


    def _determineuriparameters(self, requestedfilepath):
        if requestedfilepath.find('?') != -1:
            parameters = requestedfilepath.split('?')[1]
        else:
            parameters = ""

        return parameters


    def _determineexecutingprogram(self, clientmessageaslist):
        program = ""

        if self.fileexists():
            with open(self._filePath, 'r') as f:
                firstLineOfFile = f.readline()

            if firstLineOfFile[0:3].find('#!') != -1:
                program = firstLineOfFile[2:].replace('\n', '')

        return program


    def isvalidrequestmethod(self):
        return self._requestMethod == 'GET' or self._requestMethod == 'POST'


    def fileexists(self):
        return os.path.isfile(self._filePath)
    

    def getfiletype(self):
        return self._filePath.split('.')[-1]


    def getrequestmethod(self):
        return self._requestMethod


    def getparameters(self):
        return self._parameters


    def getexecutingprogram(self):
        return self._program


    def getfilepath(self):
        return self._filePath


    def getheader(self):
        return self._header


    def getenvironment(self):
        return self._environment


    def setheader(self, header):
        self._header = header
