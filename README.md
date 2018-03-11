# Python Web Server and Java RMI
### COMP 3010 Winter 2018 Assignment 3

## Overview
The goal for the first part of the assignment is to create a Python web server completely from scratch using only sockets and no high level structures (such as SocketServer). The server supports GET and POST requests, and serves the correct error pages to the client when necessary.

## Running the Code
The server code has been tested on Linux and Mac machines, it cannot be guaranteed to work on Windows.

### Python Server
Using a terminal, descend into the Q1-Server directory `cd Q1-Server`. From there, you may launch the server application, either with `./server.py` or `python server.py`.

The server is hard coded to run at port 15048, you may change this in the code to change the port. If the machine you are using is set up to be located by DNS, you can connect by connect to it with **address:15048/directory**. If you are testing locally, you can connect to the server with **localhost:15048/directory**.

The server is designed to serve files out of the `site` folder under Q1-Server. You may include the files you want in this folder to test what the server can handle. There are several example files in there already to test.
