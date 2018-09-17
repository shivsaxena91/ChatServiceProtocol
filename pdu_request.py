"""
CS 544 - Computer Networks
5.31.2017
Project Name: Chat Service Protocol
File: pdu_request.py

File summary:
    The purpose of this file is to create a new request object. The request object is created when the client wants to 
    fire a command and wants the server to process the command. The class has a function to convert the object into 
    an string for the request to be sent towards the server.
"""

import json

"""Requests from client are made into the PDURequest object"""
class PDURequest:
    """Constructor for PDURequest"""
    def __init__(self, version, command, parameters, channel, payload):
        self.version = version                  # Client protocol version
        self.command = command                  # 4 char command text
        self.parameters = parameters            # JSON object with parameters
        self.channel = channel                  # AC | CC | DC
        self.payload = payload                  # chat text | data

    """Serializes PDURequest object"""
    def createRequestStr(self):
        str_req = json.dumps(self.__dict__)     # serializes object to string
        str_req += "\n"                         # appends the termination character
        return str_req
