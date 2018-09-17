"""
CS 544 - Computer Networks
5.26.2017
Project Name: Chat Service Protocol
File: chat_room.py

File summary:
    The purpose of the file is to create a new chat room. When a new group is created, a chat_room object is created and 
    and added to the entire group list object. The updated list object is then converted to a string and then saved to a 
    file.
"""


"""Chat room objects stores all data pertaining to the group"""
class Chat_room:
    def __init__(self, groupName, users, admins, banned_users=[], black_users=[]):
        self.chat_name = groupName
        self.users = users
        self.admins = admins
        self.banned_users = banned_users
        self.black_users = black_users
