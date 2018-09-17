"""
CS 544 - Computer Networks
5.26.2017
Project Name: Chat Service Protocol
File: user.py

File summary:
    The purpose of the file is to transfer the details received at the server to the request handler 
"""


"""Stores details of details received at the server"""
class PDUData:
    """Constructor of PDUData"""
    def __init__(self, nick="", params=[], channel="", payload=""):
        self.nick = nick                    # Username
        self.message_parameters = params    # Parameters for the PDU
        self.channel_identifier = channel   # 3 bit channel identifier
        self.payload = payload              # Data
