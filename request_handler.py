"""
CS 544 - Computer Networks
5.29.2017
Project Name: Chat Service Protocol
File: request_handler.py

File summary:
    The purpose of this file is to handle the requests coming from the client. The requests first reach the server file and
    control is passed to this request_handler file. The RequestHandler class has the run_command function which calls
    the required function based on the command received from the client.

    The handler and client_map has been passed on so that the client_map can be updated with the relevant values. Different
    functions handles updation of client_map differently. It must be noted that the client_map's client list is being
    updated and in no point of the code is the client_map lists being replaced. This allows the client_map changes to
    be preserved when the control returns back to the server file.
"""

import json
import os
from user import User
from chat_room import Chat_room
from pdu_response import PDUResponse


"""RequestHandler class is used by the server to handle all the incoming requests from the client"""
class RequestHandler:
    """Constructor for RequestHandler class"""
    def __init__(self, req_obj=None):
        self.obj = req_obj

    ## STATEFUL - calls a different function depending on which state the PDU action belongs to ##
    """Calls the associated function of the command received
    handler -> the client socket
    client_map -> map of username and the client socket"""
    def run_command(self, command, handler, client_map):
        # Following if-else loops checks the command received and perform the associated function
        if command == "REDY":
            return self.readyAction()
        elif command == "JOIN":
            return self.joinAction(handler, client_map)
        elif command == "MSSG":
            return self.mssgAction()
        elif command == "KICK":
            return self.kickAction(client_map)
        elif command == "BANN":
            return self.banAction(client_map)
        elif command == "LIST":
            return self.listAction()
        elif command == "AUTH":
            return self.loginAuthentication(handler, client_map)
        elif command == "NWUA":
            return self.createNewUserAccount(handler, client_map)
        elif command == "CHAT":
            return self.createNewChat(handler, client_map)
        elif command == "LEVE":
            return self.leaveChat(handler, client_map)
        elif command == "VRSN":
            return self.incompatibleVersion()

    """Reads and returns contents of filename"""
    def getFileContents(self, filename):
        # If filename does not exist
        if not os.path.isfile('./' + filename):
            # Creates new file with name as filename
            file = open(filename, "w+")
            file.close()
            return ""

        # Filename exists
        else:
            # Reads file and returns file contents
            with open(filename, 'r') as myfile:
                data = myfile.read().replace('\n', '')
            return data

    """Creates new user account and saves it to file"""
    def createNewUserAccount(self, handler, client_map):
        # Fetching user account file data
        users_str = self.getFileContents(self.obj["filename"]).strip()

        # Constructing JSON object of existing data from text of the file
        if users_str is not None and users_str:
            all_users_obj = json.loads(users_str)
        else:
            all_users_obj = {"users": []}

        # Checking if user already exists
        for user_acc in all_users_obj["users"]:
            if user_acc["username"] == self.obj["username"]:
                # Username already exists
                return PDUResponse("200", {}, "", "").createResponseStr()

        # Creating new user and updating the users file
        new_user = User(self.obj["username"], self.obj["password"])

        # Updating the all_users object with new user
        all_users_obj["users"].append(json.loads(json.dumps(new_user.__dict__)))

        # Opening file in empty mode and dumps the updated data back to the file
        file = open(self.obj["filename"], "w")
        file.write(json.dumps(all_users_obj))
        file.close()

        # Updating the client_map object
        client_map["clients"].append({
            "username": self.obj["username"],
            "chat_name": "",
            "prev_chat": None,
            "handler": handler
        })

        # Creating and returning response for new user created
        return PDUResponse("110", {}, "CC", "").createResponseStr()

    """Authenticates user based on given credentials"""
    def loginAuthentication(self, handler, client_map):
        # Fetching user account file data
        users_str = self.getFileContents(self.obj["filename"]).strip()

        # Constructing JSON object of existing data from text of the file
        if users_str is not None and users_str:
            all_users_obj = json.loads(users_str)
        else:
            all_users_obj = {"users": []}

        if len(all_users_obj["users"]) == 0:
            # No user data available
            return PDUResponse("200", {}, "CC", "").createResponseStr()
        else:
            valid_user = False

            # Checking if credentials are correct
            for user_acc in all_users_obj["users"]:
                if user_acc["username"] == self.obj["username"] and user_acc["password"] == self.obj["password"]:
                    valid_user = True
                    break

            if valid_user:
                # Updating client_map object
                client_map["clients"].append({
                    "username": self.obj["username"],
                    "chat_name": "",
                    "prev_chat": None,
                    "handler": handler
                })
                # Creating and returning successful authentication response
                return PDUResponse("110", {}, "CC", "").createResponseStr()

            else:
                print "Either your username or password is incorrect"
                # Creating and returning response for invalid credentials
                return PDUResponse("200", {}, "CC", "").createResponseStr()

    """Function to check if server is alive"""
    def readyAction(self):
        # Return server is ready response
        return PDUResponse("100", {}, "CC", "Ready").createResponseStr()

    """Function responsible for allowing client to join a group"""
    def joinAction(self, handler, client_map):
        # Fetching group details data from list file
        chat_para = self.getFileContents(self.obj["list"]).strip()

        # Constructing JSON object of existing data from text of the file
        all_chat_obj = json.loads(chat_para)
        isBanned = False

        # Checking if joining user is banned from the group
        for chat in all_chat_obj["chats"]:
            if chat["chat_name"] == self.obj["chat_name"] and self.obj["username"] in chat["banned_users"]:
                isBanned = True
                break

        # Not banned
        if not isBanned:
            # Update the group list file
            file = open(self.obj["list"], "w")
            file.write(json.dumps(all_chat_obj))
            file.close()

            # Update the client_map
            for client in client_map["clients"]:
                if client["username"] == self.obj["username"]:
                    prev_chat = client["chat_name"]
                    client["chat_name"] = self.obj["chat_name"]     # set to new chat
                    client["prev_chat"] = prev_chat                 # set to previous chat
                    client["handler"] = handler

            parameters = {"username": self.obj["username"], "chat_name": self.obj["chat_name"]}

            # Creating and returning group joined successfully response
            return PDUResponse("180", parameters, "CC", self.obj["username"] + " has joined the group").createResponseStr()

        else:
            parameters = {"username": self.obj["username"], "chat_name": self.obj["chat_name"]}
            # Creating and returning group joining failed response
            return PDUResponse("240", parameters, "CC", "You are banned from joining this group").createResponseStr()

    """Receive message from client and creating response to send to all other clients in the group"""
    def mssgAction(self):
        # Creating and returning message response
        return PDUResponse("140", {}, "DC", self.obj["payload"]).createResponseStr()

    """Function for kicking username from a group. Can only be performed by an admin. Username can rejoin"""
    def kickAction(self, client_map):
        # Fetching group details data from list file
        groups_str = self.getFileContents(self.obj["list"]).strip()

        # Constructing JSON object of existing data from text of the file
        if groups_str is not None and groups_str:
            groups_obj = json.loads(groups_str)
        else:
            groups_obj = {"chats": []}

        isAdmin = False

        # Checking if client is admin
        for chat in groups_obj["chats"]:
            if chat["chat_name"] == self.obj["chat_name"]:
                for admin in chat["admins"]:
                    if admin == self.obj["username"]:
                        isAdmin = True
                        break
                break

        if isAdmin:
            # Updating the client_map object
            for client in client_map["clients"]:
                if client["username"] == self.obj["kicked_user"]:
                    prev_chat = client["chat_name"]
                    client["chat_name"] = ""            # emptying current chat
                    client["prev_chat"] = prev_chat     # setting to previous chat
                    client["handler"].chat_name = ""

            parameters = {"kicked_user": self.obj["kicked_user"]}

            # Creating and returning successfully kicked response
            return PDUResponse("192", parameters, "CC", self.obj["kicked_user"] + " has been kicked from the group")\
                .createResponseStr()

        else:
            # Creating and returning failed to kick response
            return PDUResponse("260", {"username": self.obj["username"]}, "CC", "You are not the admin of this group") \
                .createResponseStr()

    """Function for banning username from a group. Can only be performed by an admin. Username cannot rejoin"""
    def banAction(self, client_map):
        # Loading both user credentials and group details file
        users_str = self.getFileContents(self.obj["filename"]).strip()
        groups_str = self.getFileContents(self.obj["list"]).strip()

        # Construction JSON object from the user credentials string
        if users_str is not None and users_str:
            all_users_obj = json.loads(users_str)
        else:
            all_users_obj = {"users": []}

        # Construction JSON object from the group details string
        if groups_str is not None and groups_str:
            groups_obj = json.loads(groups_str)
        else:
            groups_obj = {"chats": []}

        isAdmin = False

        # Checking if admin
        for chat in groups_obj["chats"]:
            if chat["chat_name"] == self.obj["chat_name"]:
                for admin in chat["admins"]:
                    if admin == self.obj["username"]:
                        isAdmin = True

                        # The client is admin, thus can ban the user. Adding to list of banned users of the group
                        chat["banned_users"].append(self.obj["banned_user"])
                        break
                break

        if isAdmin:
            # Updating users account
            for user_acc in all_users_obj["users"]:
                if user_acc["username"] == self.obj["banned_user"]:
                    # User accounts maintaining list of groups banned from
                    user_acc["bannedGroups"].append(self.obj["chat_name"])
                    break

            # Writing back the updated user accounts and group details to the files
            file = open(self.obj["filename"], "w")
            file.write(json.dumps(all_users_obj))
            file.close()

            file = open(self.obj["list"], "w")
            file.write(json.dumps(groups_obj))
            file.close()

            # Updating the client_map object
            for client in client_map["clients"]:
                if client["username"] == self.obj["banned_user"]:
                    prev_chat = client["chat_name"]
                    client["chat_name"] = ""
                    client["prev_chat"] = prev_chat
                    client["handler"].chat_name = ""

            # Creating and returning a successful ban response
            return PDUResponse("191", {"banned_user": self.obj["banned_user"]}, "CC",
                               self.obj["banned_user"] + " has been banned from the group").createResponseStr()

        else:
            # Creating and returning a failed to ban response
            return PDUResponse("250", {"username": self.obj["username"]}, "CC", "You are not the admin of this group")\
                .createResponseStr()

    """Returns list of existing groups available in the server"""
    def listAction(self):
        # Getting contents of group details file
        chat_para = self.getFileContents(self.obj["list"]).strip()

        if chat_para is not None and chat_para:
            # Creating JSON object from group details string
            all_chat_obj = json.loads(chat_para)
            groupList = []
            for user_acc in all_chat_obj["chats"]:
                groupList.append(user_acc["chat_name"])

            # Creating and returning successful group fetch response
            return PDUResponse("130", {"username": self.obj["username"]}, "", groupList).createResponseStr()
        else:
            # Creating and returning failed group fetch response
            return PDUResponse("240", {"username": self.obj["username"]}, "", "There are currently no groups").createResponseStr()

    """Creates new group and maintains the groups in a file"""
    def createNewChat(self, handler, client_map):
        # Load group details file
        chat_para = self.getFileContents(self.obj["list"]).strip()

        # Construct JSON from group details string
        if chat_para is not None and chat_para:
            all_chat_obj = json.loads(chat_para)
        else:
            all_chat_obj = {"chats": []}

        # Checking if group already exists
        for groupChat in all_chat_obj["chats"]:
            if groupChat["chat_name"] == self.obj["chat_name"]:
                return PDUResponse("230", {}, "", "Group name already exists").createResponseStr()

        users = [self.obj["username"]]
        admins = [self.obj["username"]]
        new_user = Chat_room(self.obj["chat_name"], users, admins)

        # Updating the all_chat_obj with the new user
        all_chat_obj["chats"].append(json.loads(json.dumps(new_user.__dict__)))

        # Updating group details
        file = open(self.obj["list"], "w")
        file.write(json.dumps(all_chat_obj))
        file.close()

        # Updating the user accounts file
        f = open("user_accounts.txt")
        data = f.read().replace('\n', '').strip()
        all_users_obj = json.loads(data)
        for user_acc in all_users_obj["users"]:
            if user_acc["username"] == self.obj["username"]:
                # Retrieving admins
                adminGroups = user_acc["adminGroups"]
                for i in range(0, len(adminGroups)):
                    if adminGroups[i] == self.obj["chat_name"]:
                        break
                    if len(adminGroups) - 1 == i:
                        # Adding to list of admins
                        adminGroups.append(self.obj["chat_name"])
                if len(adminGroups) == 0:
                    # Adding to list of admins
                    adminGroups.append(self.obj["chat_name"])
                break

        f.close()

        # Writing updated user accounts data back to the file
        file = open("user_accounts.txt", "w")
        file.write(json.dumps(all_users_obj))
        file.close()

        # Updating the client_map object
        for client in client_map["clients"]:
            if client["username"] == self.obj["username"]:
                client["chat_name"] = self.obj["chat_name"]
                client["prev_chat"] = ""
                client["handler"] = handler

        # Creating and returning group created successfully response
        return PDUResponse("170", {}, "", "").createResponseStr()

    """Function responsible for removing user from chat room"""
    def leaveChat(self, handler, client_map):

        # Updating the client_map object
        for client in client_map["clients"]:
            if client["username"] == self.obj["username"]:
                prev_chat = client["chat_name"]
                client["chat_name"] = ""
                client["prev_chat"] = prev_chat
                client["handler"] = handler
                break

        # Creating and returning a left group successfully response
        return PDUResponse("190", {"username": self.obj["username"]}, "",
                           self.obj["username"] + " has left the chat room").createResponseStr()

    """Function responsible for returning incompatible versions response"""
    def incompatibleVersion(self):
        # Creating and returning incompatible version response
        return PDUResponse("330", {}, "CC", "Server is running on a different protocol version").createResponseStr()
