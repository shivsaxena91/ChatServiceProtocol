"""
CS 544 - Computer Networks
5.23.2017
Project Name: Chat Service Protocol
File: server.py

File summary:
    The purpose of the file is to create a working server which listens at a specified port. The client will have to
    connect to the server using the server IP and the port that the server is listening to. The server receives the
    commands from the client, and it is the responsibility of the server to decide what to do with the request.

    Async_chat has been used to detect the terminating character/s in the request stream. Once the server receives the
    terminating character/s, the found_terminator function gets called after which further request processing can be
    performed. Additionally, async_chat keeps updating the chat_room object with the clients IP address as well as the
    port number whenever a new client connects with the server.

    The client_map object is critical for the proper functioning of the protocol. The chat_room object is updated by
    async chat. It has all the IP addresses and port numbers of all the clients that are connected to the server. Our
    code makes use of the chat_room object to update the client_map. The client_map is essentially a map between
    clients username and the socket details (i.e. the clients IP and port no) in the chat_room.

"""

import asynchat
import asyncore
import socket
import json
import request_handler as reqh

## CONCURRENT - the chat_room map accepts and stores multiple client objects ##
chat_room = {}          # chat_room is being updated by async chat
client_map = {          # client_map is being updated by the server code
    "clients": []       # "clients" stores a list of individual clients that are authenticated by the server
}

"""A new ChatHandler object is created each time a client connects with the server"""
class ChatHandler(asynchat.async_chat):

    """Constructor of ChatHandler"""
    def __init__(self, sock, server_obj):
        # Initialises async_chat with the clients socket as its parameter. chat_room is passed along for it to be updated with the new client details
        asynchat.async_chat.__init__(self, sock=sock, map=chat_room)

        # Setting up the terminator. So if the response stream ends with this terminator, found_terminator function is called
        self.set_terminator('\n')

        # Async_chat stores all incoming request streams in the buffer until the terminator has been received
        self.buffer = []

        # This is the ChatServer classes object
        self.server_obj = server_obj

    """Collects all incoming data from the client until the terminator string has been received"""
    def collect_incoming_data(self, data):
        self.buffer.append(data)

    ## STATEFUL - calls the processRequest function ##
    """This function is called by async_chat when the terminator, set by set_terminator, is found in the request stream"""
    def found_terminator(self):
        # Joins all the values in the buffer as a single string
        msg = ''.join(self.buffer)

        # Converts the serialized message received from the client back to a JSON object
        req_obj = json.loads(msg)

        # checking if client and the server are running on the same version of the protocol
        if req_obj["version"] == self.server_obj.getVersion():
            # processRequest processes the request by calling the associated function for the command sent by the client
            # The variable response is a serialized string that is to be sent to all appropriate clients
            response = self.server_obj.processRequest(req_obj, self)

            # response_obj is the JSON object of the response string
            response_obj = json.loads(response)
        else:
            # The versions of the client and server is not the same. Returns response code associated with incompatible version
            response = self.server_obj.incompatibleVersion()

        # Iterating through client_map i.e. every client that is connected on the server
        for client in client_map["clients"]:
            # When username has not been set, only NWUA and AUTH are valid request commands from the client
            if client["username"] == "":
                if req_obj["command"] in ["NWUA", "AUTH"]:      # ignore all other commands
                    # pushes the response to the client IP and port number. client["handler"] has those client details
                    client["handler"].push(response)

            # When client has not joined a group or if banned, kicked or has moved out from group
            elif client["chat_name"] == "" and client["prev_chat"] != req_obj["parameters"]["chat_name"]:
                # When chat_name = "", only AUTH, LIST, CHAT, JOIN, REDY are valid commands from the client.
                if req_obj["command"] in ["AUTH", "LIST", "CHAT", "REDY"]:
                    client["handler"].push(response)

                # If command is JOIN, the response needs to be pushed only when response_code is 240 i.e. when joining a group has failed
                elif response_obj["response_code"] == "240":
                    client["handler"].push(response)

            # chat_name is set to an empty string when a client is kicked, banned or has left the group. Thus, the responses
            # that needs to be sent to such clients would be based on the prev_chat attribute. Prev_chat stores the
            # chat name of the previous chat that the client was connected to.
            elif client["chat_name"] == "" and client["prev_chat"] == req_obj["parameters"]["chat_name"]:
                # chat_name can also be empty when commands form the client is KICK, BANN and LEVE
                if req_obj["command"] in ["JOIN", "KICK", "BANN", "LEVE"]:
                    client["prev_chat"] = None
                    client["handler"].push(response)

            # Sending the response to all the other clients of the group
            elif client["chat_name"] == req_obj["parameters"]["chat_name"]:
                client["handler"].push(response)

        # Clearing the buffer array to get ready for the next request
        self.buffer = []

## SERVICE - hardcoding the port that will serve as the endpoint on the server ##
"""ChatServer is the class that sets up the server and is responsible for listening to the incoming requests from the client"""
class ChatServer(asyncore.dispatcher):
    __host = "127.0.0.1"                    # IP of the server
    __port = 12345                          # The server will listen to incoming requests on this port
    __user_file = "./user_accounts.txt"     # File that stores the user credentials
    __list = "./list.txt"                   # File that stores the group / chat room details
    __version = 1.0                         # Server protocol version

    """Constructor of ChatServer class"""
    def __init__(self):
        # Initializes asyncore dispatcher
        asyncore.dispatcher.__init__(self, map=chat_room)
        # Creates a new socket
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binds server ip and port number
        self.bind((ChatServer.__host, ChatServer.__port))
        # Start listening to requests from the client
        self.listen(5)
        print 'Server listening on ', ChatServer.__host, ':', ChatServer.__port

    """Returns version number of servers protocol"""
    def getVersion(self):
        return self.__version

    ## CONCURRENT - the server accepts multiple connections and stores each new client's details in the client_map ##
    """Asyncore calls this function when a client makes a connection with the server"""
    def handle_accept(self):
        # pair is a tuple of the client socket and port number
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)

            # Creating a new instance of ChatHandler when a new client connects with the server
            handler = ChatHandler(sock, self)

            # Updating the client_map with the details of the new client that has connected with the server.
            # Only the handler field is filled as the username, chat_name and prev_chat details won't exist when the
            # client first connects with the server
            client_map["clients"].append({
                "username": "",
                "chat_name": "",
                "prev_chat": "",
                "handler": handler
            })

    """Processes the requests from the client i.e. appropriate function is called on the RequestHandler class based
    on the command"""
    def processRequest(self, req_obj, handler):
        command = req_obj["command"]

        # Preparing a JSON object, obj, to be used by RequestHandler functions with different parameters based on the command
        obj = {
            "username": req_obj["parameters"]["username"]
        }
        if command == "AUTH" or command == "NWUA":
            obj["password"] = req_obj["parameters"]["password"]
            obj["filename"] = self.__user_file

        elif command == "LIST":
            obj["list"] = self.__list

        elif command == "CHAT":
            obj["chat_name"] = req_obj["parameters"]["chat_name"]
            obj["list"] = self.__list

        elif command == "JOIN":
            obj["chat_name"] = req_obj["parameters"]["chat_name"]
            obj["list"] = self.__list

        elif command == "BANN":
            obj["chat_name"] = req_obj["parameters"]["chat_name"]
            obj["banned_user"] = req_obj["parameters"]["banned_user"]
            obj["filename"] = self.__user_file
            obj["list"] = self.__list

        elif command == "KICK":
            obj["chat_name"] = req_obj["parameters"]["chat_name"]
            obj["kicked_user"] = req_obj["parameters"]["kicked_user"]
            obj["filename"] = self.__user_file
            obj["list"] = self.__list

        elif command == "MSSG":
            obj["payload"] = req_obj["payload"]

        reqh_obj = reqh.RequestHandler(obj)
        # Returns response string
        return reqh_obj.run_command(command, handler, client_map)

    def incompatibleVersion(self):
        reqh_obj = reqh.RequestHandler()
        # Returns response string
        return reqh_obj.run_command("VRSN", "", "")

# initializing the ChatServer class
server = ChatServer()
# Enter a polling loop that terminates after all channels have been closed
asyncore.loop(map=chat_room)
