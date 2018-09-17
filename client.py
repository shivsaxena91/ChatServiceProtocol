"""
CS 544 - Computer Networks
5.23.2017
Project Name: Chat Service Protocol
File: client.py

File summary:
    The purpose of this file is to create new clients and manage the states that the client is in. The client makes use
    of async chat to send and receive data to and from the server. The client needs to know the IP of the server and the
    port that the server is listening on to make the connection.

    Async_chat has been used to detect the terminating character/s in the request stream. Once the server receives the
    terminating character/s, the found_terminator function gets called after which further request processing can be
    performed.

    The ChatClient is primarily responsible for sending requests to the server and receiving responses from the server.
    The server responds in pre-defined response codes. The ChatClient looks at the response code and decides on how to
    deal with the response code.
"""


import asynchat
import asyncore
import socket
import threading
import json
from pdu_request import PDURequest
from response_handler import ResponseHandler
import pdu_data

## CLIENT SPECIFICATION - hardcoding the port that the server is listening on ##
"Each time the client uses the system, the ChatClient class is instantiated"
class ChatClient(asynchat.async_chat):
    __host = "127.0.0.1"    # host IP
    __port = 12345          # port that server listens to
    __version = 1.0         # client protocol version

    """constructor for ChatClient"""
    def __init__(self):

        # initializing async_chat
        asynchat.async_chat.__init__(self)

        # creates new socket
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        # Setting up the terminator. So if the response stream ends with this terminator, found_terminator function is called
        self.set_terminator('\n')

        # Async_chat stores all incoming request streams in the buffer until the terminator has been received
        self.buffer = []

        # Following attributes stores client specific data
        self.obj = {}
        self.username = ""
        self.chat_name = ""
        self.groupNames = []

        """The following attributes are used as while loop terminators. The client sends a request to the server, but the
        response does not return to the same location where the request was sent. Whereas, it reaches found_terminator
        when the response contains the terminator. In the mean while, a while loop is started where the request is sent,
        thus halting the execution of the code at that location. The while loop terminates only when the following
        attributes values are changed in the found_terminator function"""

        # authentication_complete is set to true when authentication has been complete and response is received from the server
        self.authentication_complete = False

        # create_group_resp_recv is set to true when the servers 'create group' function returns a response back to the client
        self.create_group_resp_recv = False

        # groupNames_received is set to true when the client receives the group names from the server
        self.groupNames_received = False

        # ban_complete is set to true when the banning function has been called and a response has been received from the server
        self.ban_complete = False

        # ban_allowed is set to true when banning is valid and remains false if banning is invalid
        self.ban_allowed = False

        # move_out is set to true when the server removes the client from a group and the client receives a response from the server
        self.moved_out = False

    """Makes connection to the server based on host and port no"""
    def connect_to_server(self):
        # Makes connection to the server given the host ip and the port no
        self.connect((ChatClient.__host, ChatClient.__port))

    """Creates object of class PDURequest and serializes the object to a string.
    The string terminates with '\n' so that the servers found_terminator function would be called on invoking push"""
    def sendPDURequest(self, command, parameters, channel, payload):
        str_send = PDURequest(self.__version, command, parameters, channel, payload).createRequestStr()
        self.push(str_send)

    """Collects all incoming data from the server until the terminator string has been received"""
    def collect_incoming_data(self, data):
        self.buffer.append(data)

    ## STATEFUL - invocation of the processResponse() method ##
    """Called when response has the value set in set_terminator in the clients constructor"""
    def found_terminator(self):
        # Joins all the values in the buffer as a single string
        resp_str = ''.join(self.buffer)

        # Clearing the buffer array to get ready for the next response
        self.buffer = []

        # Converts the serialized message received from the server back to a JSON object
        resp_obj = json.loads(resp_str)

        """The following block of if-else loops are for handling different response codes separately.
        The response from the server can be a positive or a negative response. Thus the actions to be performed by the
        client after receiving a response depends to the response code"""

        # When has successfully been authenticated into the system
        if resp_obj["response_code"] == "110":
            self.obj["authenticated"] = True
            self.authentication_complete = True

        # When the list of groups have been returned from the server
        elif resp_obj["response_code"] == "130":
            if self.username == resp_obj["parameters"]["username"]:
                # The group names are extracted from the payload
                self.groupNames = resp_obj["payload"]

                self.processResponse(resp_obj)

                self.obj["group_fetch_success"] = True
                self.groupNames_received = True

        # When the client receives a message from the server
        elif resp_obj["response_code"] == "140":
            # The message is extracted from the payload
            chat = resp_obj["payload"]

            # Condition for not printing the message on the senders console
            if self.username == chat[1: len(self.username) + 1]:
                return
            else:
                self.processResponse(resp_obj)
                # comma added to allow next print to be on the same line
                print("-> "),

        # When group has been created successfully
        elif resp_obj["response_code"] == "170":
            self.obj["groupCreated"] = True
            self.create_group_resp_recv = True

        # When the client successfully joins a group
        elif resp_obj["response_code"] == "180":
            if self.username == resp_obj["parameters"]["username"]:
                self.chat_name = resp_obj["parameters"]["chat_name"]
            self.processResponse(resp_obj)

        # When a client successfully leaves a group
        elif resp_obj["response_code"] == "190":
            self.processResponse(resp_obj)
            if resp_obj["parameters"]["username"] == self.username:
                self.moved_out = True

        # When banning a user was successful
        elif resp_obj["response_code"] == "191":
            if resp_obj["parameters"]["banned_user"] == self.username:
                self.chat_name = ""
            self.processResponse(resp_obj)

        # When kicking a user was successful
        elif resp_obj["response_code"] == "192":
            if resp_obj["parameters"]["kicked_user"] == self.username:
                self.chat_name = ""
            self.processResponse(resp_obj)

        # When authentication to the system failed
        elif resp_obj["response_code"] == "200":
            self.obj["authenticated"] = False
            self.authentication_complete = True

        # When group could not be created successfully
        elif resp_obj["response_code"] == "230":
            self.obj["groupCreated"] = False
            self.create_group_resp_recv = True

        # When joining group action failed
        elif resp_obj["response_code"] == "240":
            if self.username == resp_obj["parameters"]["username"]:
                self.processResponse(resp_obj)

                self.obj["group_fetch_success"] = False
                self.groupNames_received = True

        # When banning user action failed
        elif resp_obj["response_code"] == "250":
            if resp_obj["parameters"]["username"] == self.username:
                self.processResponse(resp_obj)

        # When kicking user action failed
        elif resp_obj["response_code"] == "260":
            if resp_obj["parameters"]["username"] == self.username:
                self.processResponse(resp_obj)

        # When server and client versions are incompatible
        elif resp_obj["response_code"] == "330":
            self.processResponse(resp_obj)
            self.handle_close()

        # For all other response codes
        else:
            self.processResponse(resp_obj)

    ## STATEFUL - calls the ResponseHandler to parse PDUs ##
    """Processes the response from the server i.e. appropriate function is called on the ResponseHandler class based on the response code"""
    def processResponse(self, resp_obj):
        resp_code = resp_obj["response_code"]
        # Setting up PDUData object to be used in response handling
        obj = pdu_data.PDUData()
        obj.payload = resp_obj["payload"]

        resh_obj = ResponseHandler(obj)
        # Calls the associated function for the received response code
        return resh_obj.runResponseCodeAction(resp_code)

    """Async chat calls this if the client has thrown an unhandled error or if the client logs out from the system"""
    def handle_close(self):
        self.close()
        print "Your connection has been terminated"

    """This function is responsible for clients authentication, creation or joining groups"""
    def initiateDialog(self):

        print "Welcome to our CSP system. To continue, select one of the following"

        while True:

            print "1 -> Login"
            print "2 -> Sign up"
            user_input = raw_input("-> ")

            # For login
            if user_input == "1":
                self.authentication_complete = False

                # Fetching user input for username and password
                username = raw_input("username-> ")
                password = raw_input("password-> ")

                # Setting up parameters
                creds = {"username": username, "password": password, "chat_name": ""}

                # Send request to perform authentication
                self.sendPDURequest("AUTH", creds, "CC", "")

                # Wait for server response. Value of self.authentication_complete set to true in found_terminator
                while not self.authentication_complete:
                    pass

                if self.obj["authenticated"]:
                    self.username = username
                    print("Login successful")
                    self.createOrFetchGroups()
                    break
                else:
                    print "Either your username or password is incorrect"
                    continue

            # For creating new account
            elif user_input == "2":
                self.authentication_complete = False

                # Fetching user input for username and password
                username = raw_input("choose username-> ")
                password = raw_input("choose password-> ")

                # Setting up parameters
                creds = {"username": username, "password": password, "chat_name": ""}

                # Send request to create new user account
                self.sendPDURequest("NWUA", creds, "CC", "")

                # Wait for server response. Value of self.authentication_complete set to true in found_terminator
                while not self.authentication_complete:
                    pass

                if self.obj["authenticated"]:
                    self.username = username
                    print("Account created")
                    self.createOrFetchGroups()
                    break
                else:
                    print "Username already exists"
                    continue
            else:
                print "Invalid input, try again."
                continue

    """Function responsible for fetching available groups or creating a new group"""
    def createOrFetchGroups(self):
        while True:
            print "1 -> Join available groups"
            print "2 -> Create new group"
            user_input = raw_input("-> ")

            # Join existing group
            if user_input == "1":
                para = {"username": self.username, "chat_name": ""}

                # Send request to fetch existing groups
                self.sendPDURequest("LIST", para, "CC", "")

                # Wait for server response. Value of self.groupNames_received set to true in found_terminator
                while not self.groupNames_received:
                    pass

                if self.obj["group_fetch_success"]:
                    self.joinGroup(self.username)

                    # Resetting values
                    self.obj["group_fetch_success"] = False
                    self.groupNames_received = False
                    self.groupNames = []
                    break
                else:
                    continue

            # Create new group
            elif user_input == "2":
                print "Enter Group name"
                groupName = raw_input("-> ")

                if groupName.strip() == "":
                    print "Group name cannot be 0 characters"
                    continue

                para = {"username": self.username, "chat_name": groupName}

                # Send request to create a new group
                self.sendPDURequest("CHAT", para, "CC", "")

                # Wait for server response. Value of self.create_group_resp_recv set to true in found_terminator
                while not self.create_group_resp_recv:
                    pass

                if self.obj["groupCreated"]:
                    self.chat_name = groupName
                    print("Group Created. You are the admin of this group. You have joined the group")
                    break
                else:
                    print "Group already exists"
                    continue

            else:
                print "Invalid input"
                continue

    """Function responsible for joining a selected group"""
    def joinGroup(self, username):
        while True:
            user_input = raw_input("-> ")
            chatFound = False

            # Displaying the group names as a list
            for i in range(0, len(self.groupNames)):
                try:
                    number = int(user_input)
                except ValueError:
                    print "Please enter a valid input"
                    break
                else:
                    if number == i + 1:
                        # Setting up parameters
                        para = {"username": username, "chat_name": self.groupNames[int(user_input) - 1]}

                        # Send request to join a group
                        self.sendPDURequest("JOIN", para, "CC", "")
                        chatFound = True
                    elif i == len(self.groupNames)-1 and not chatFound:
                        print "Please enter a valid input"
                        continue

            # Resetting for next fetch
            self.groupNames = []

            if not chatFound:
                continue
            else:
                break

    """Display list of commands that can be fired by the client. Function is called when client types in -help"""
    def displayOptions(self):

        if self.username == "":
            print "Log in first"
        else:
            print "Help         : -help"
            print "Logout       : -logout"

            if self.chat_name == "":
                print "Join group   : -join"

            if self.chat_name != "":
                print "Exit Group   : -moveout"

            print "Kick User    : -kick username"
            print "Ban User     : -ban username"

    """Function is responsible for displaying the chat console"""
    def chatConsole(self):
        while True:
            msg = raw_input('-> ')

            # When client wants to logout from the system
            if msg == "-logout":
                self.handle_close()
                break

            # When client wants to see the list of commands that can be fired
            elif msg == "-help":
                self.displayOptions()

            # When # client wants to leave the group
            elif msg == "-moveout":
                # Send leave group request
                self.sendPDURequest("LEVE", {"username": self.username, "chat_name": self.chat_name}, "CC", "")

                while not self.moved_out:
                    pass

                # Resetting values
                self.moved_out = False
                self.groupNames = []

                print ""
                self.createOrFetchGroups()

            # When client wants to join a new group
            elif msg == "-join":
                if self.chat_name != "":
                    print "First run -moveout"
                else:
                    self.groupNames = []
                    self.createOrFetchGroups()

            # When an admin client who wants to kick a user from the chat (user can rejoin)
            elif "-kick" in msg:
                if self.chat_name == "":
                    print "You are not part of a group right now. Join a group first"
                    continue

                kick_user = msg.strip().split(" ")[1:]
                if len(kick_user) == 0:
                    print "Missing parameters. Syntax ==>  -kick username"
                elif len(kick_user) > 1:
                    print "Too many parameters. Syntax ==>  -kick username"
                elif kick_user[0] == self.username:
                    print "You cannot kick yourself"
                else:
                    parameters = {"username": client.username, "chat_name": client.chat_name, "kicked_user": kick_user[0]}

                    # Send kick request
                    self.sendPDURequest("KICK", parameters, "AC", "")

            # When admin client who wants to ban a user from the chat (user can't rejoin)
            elif "-ban" in msg:
                if self.chat_name == "":
                    print "You are not part of a group right now. Join a group first"
                    continue

                banned = msg.strip().split(" ")[1:]
                if len(banned) == 0:
                    print "Missing parameters. Syntax ==>  -ban username"
                elif len(banned) > 1:
                    print "Too many parameters. Syntax ==>  -ban username"
                elif banned[0] == self.username:
                    print "You cannot ban yourself"
                else:
                    parameters = {"username": client.username, "chat_name": client.chat_name, "banned_user": banned[0]}

                    # Send ban request
                    self.sendPDURequest("BANN", parameters, "AC", "")

            # All other chats sent by the client
            else:
                if self.chat_name == "":
                    print "You are not connected to any group. Try -join to join another group"
                    continue
                elif msg.strip() == "":
                    continue

                msg = "(" + self.username + ") " + msg

                # Send message request
                self.sendPDURequest("MSSG", {"username": self.username, "chat_name": self.chat_name}, "DC", msg)

# Creating a new client
client = ChatClient()

# Connect to the server
client.connect_to_server()

# Start thread
comm = threading.Thread(target=asyncore.loop)
comm.daemon = True
comm.start()

client.initiateDialog()
client.chatConsole()
