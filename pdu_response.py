"""
CS 544 - Computer Networks
5.31.2017
Project Name: Chat Service Protocol
File: pdu_response.py

File summary:
    The purpose of this file is to create a new response object. The response object is created when the server wants to 
    send a response to the client. The class has a function to convert the object into an string for the resposne to be 
    sent towards the client.
"""

import json


"""Responses from server are made into the PDUResponse object"""
class PDUResponse:

    __version = 1.0     # Servers protocol version

    """Constructor of PDUResponse"""
    def __init__(self, code, parameters, channel, payload):
        self.version = PDUResponse.__version
        self.response_code = code                   # 3 digit response code | string
        self.parameters = parameters                # JSON obj of parameters
        self.channel = channel                      # AC | CC | DC
        self.payload = payload                      # Data

    """Serializes PDUResponse object"""
    def createResponseStr(self):
        str_resp = json.dumps(self.__dict__)        # Serialization
        str_resp += "\n"                            # Termination character
        return str_resp
