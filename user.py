"""
CS 544 - Computer Networks
5.26.2017
Project Name: Chat Service Protocol
File: user.py

File summary:
    The purpose of the file is to create a new client. When a new client is created, a new user object is created and 
    and added to the entire user list object. The updated user object is then converted to a string and then saved to a 
    file.
"""

"""User objects stores data pertaining to the client"""
class User:
    """Constructor of User class"""
    def __init__(self, username, password, adminGroups=[], bannedGroups=[]):
        self.username = username
        self.password = password
        self.adminGroups = adminGroups      # List of groups that the client is an admin
        self.bannedGroups = bannedGroups    # List of groups that the client is banned from
