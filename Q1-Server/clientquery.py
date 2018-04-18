#!/usr/bin/python

import os

class ClientQuery:
    def __init__(self, clientmessageaslist):
        self._requestMethod = self._determinerequestmethod(clientmessageaslist[0])
        fileRequested = self._determinerequestedresourcepath(clientmessageaslist[0])
        self._filePath = self._determinerelativefilepath(fileRequested)
        if self._requestMethod == 'GET':
            self._parameters = self._determineuriparameters(fileRequested)
        elif self._requestMethod == 'POST':
            self._parameters = clientmessageaslist[-1]


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


    def isvalidrequestmethod(self):
        return self._requestMethod == 'GET' or self._requestMethod == 'POST'


    def fileexists(self):
        return os.path.isfile(self._filePath)
    

    def fileisscript(self):
        return self._filePath.find('.cgi') != -1


    def getrequestmethod(self):
        return self._requestMethod


    def getfilepath(self):
        return self._filePath
