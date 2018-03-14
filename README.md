# Python Web Server and Java RMI
### COMP 3010 Winter 2018 Assignment 3

## Overview
The goal for the first part of the assignment is to create a Python web server completely from scratch using only sockets and no high level structures (such as SocketServer). The server supports GET and POST requests, and serves the correct error pages to the client when necessary. The second part of the assignment involves reworking a socket server/client program into an RMI server/client program. The RMI client is able to get the time by connecting to a remote RMI registry updated regularly by a server.

## Running the Code
The server and RMI code has been tested on Linux and Mac machines only, the code cannot be guaranteed to work on Windows.

### Python Web Server (Question 1)
Using a terminal, descend into the Q1-Server directory: `cd Q1-Server`. From there, you may launch the server application, either with `./server.py` or `python server.py`.

The server is hard coded to run at port 15048, you may change this in the code to change the port. If the machine you are using is set up to be located by DNS, you can connect by connect to it with **example.com:15048/directory** in your web browser (substituting example.com for the host name). If you are testing locally, you can connect to the server with **localhost:15048/directory** in your web browser.

The server is designed to serve files out of the `site` folder under Q1-Server. You may include the files you want in this folder to test what the server can handle. There are several example files in there already to test. You can direct the browser to directories or files and the server will do its best to locate what you want, but if you specify a directory and there is no index.html in it, you will get a 404 page.

### Java RMI Server/Client (Question 2)
Using a terminal, descend into the Q2-RMI directory: `cd Q2-RMI`. There are two scripts in that directory, one to run the server and one to run the client, called `runserver` and `runclient`, respectively. There are two possible ways to test the code. You may a) test the server locally, or b) test the server remotely. In both cases, make sure the server is started before the client.

To test the server locally, run the server on your local machine and sepcify a port: `./runserver <port>`. This builds the files and starts up the registry. To connect to the server locally, start the client on the same machine: `./runclient localhost <same-port>`. The client should output the date.

To test the server remotely, run the server with whichever port you like on a remote machine: `./runserver <port>`. To connect to the server remotely, start the client on a different machine: `./runclient <remote-name> <same-port>`. The client should output the date.

**Note:** If you run the server in the background, you will need to kill the RMI registry separate from the server. I use `lsof -i :port` to find the registry and kill the process associated with it.
