"""
CS 544 - Computer Networks
5.29.2017
Project Name: Chat Service Protocol
File: response_handler.py

File summary:
    The purpose of this file is to handle the responses coming from the server. The responses first reach the client file
    and control is passed to this response_handler file. The ResponseHandler class has the runResponseCodeAction function
    which calls the required function based on the response code received from the server.

    Almost all of the functions defined in this class just involves printing the payload that has been returned back
    from the server
"""

"""ResponseHandler class is used by the client to handle all the incoming responses from the server.
Almost all functions of ResponseHandler would be printing something to notify the client"""
class ResponseHandler:

    """Constructor for ResponseHandler"""
    def __init__(self, obj):
        self.obj = obj

    ## STATEFUL - calls a different function to handle each request being sent from a different state ##
    """Calls the associated function of the response code received"""
    def runResponseCodeAction(self, resp_code):
        if resp_code == "100":
            return self.acknowledgeConnectionAction(self.obj)
        elif resp_code == "130":
            return self.receiveListOfChannelsAction()
        elif resp_code == "140":
            return self.receiveQueuedMessagesAction()
        elif resp_code == "180":
            return self.groupJoinedAction()
        elif resp_code == "190":
            return self.leftGroupAction()
        elif resp_code == "191":
            return self.banSuccessAction()
        elif resp_code == "192":
            return self.kickSuccessAction()
        elif resp_code == "230":
            return self.groupCreationFailedAction()
        elif resp_code == "240":
            return self.joinGroupFailedAction()
        elif resp_code == "250":
            return self.banFailedAction()
        elif resp_code == "260":
            return self.kickFailedAction()
        elif resp_code == "330":
            return self.incompatibleVersionAction()

    """Prints payload"""
    def banSuccessAction(self):
        print "****", self.obj.payload, "****"

    """Prints payload"""
    def banFailedAction(self):
        print "****", self.obj.payload, "****"

    """Prints payload"""
    def kickSuccessAction(self):
        print "****", self.obj.payload, "****"

    """Prints payload"""
    def kickFailedAction(self):
        print "****", self.obj.payload, "****"

    """Prints payload"""
    def acknowledgeConnectionAction(self, data):
        print self.obj.payload

    """Prints list of groups"""
    def receiveListOfChannelsAction(self):
        print "Choose Group"
        chatList = self.obj.payload
        for i in range(0, len(chatList)):
            print i+1, ":", chatList[i]

    """Prints payload"""
    def receiveQueuedMessagesAction(self):
        print self.obj.payload

    """Prints payload"""
    def groupCreationFailedAction(self):
        # print self.obj.payload
        pass

    """Prints payload"""
    def joinGroupFailedAction(self):
        print "****", self.obj.payload, "****"

    """Prints payload"""
    def groupJoinedAction(self):
        print "****", self.obj.payload, "****"
        # , allows next print to be on the same line
        print "-> ",

    """Prints payload"""
    def leftGroupAction(self):
        print "****", self.obj.payload, "****"
        print ""

    """Prints payload"""
    def incompatibleVersionAction(self):
        print "****", self.obj.payload, "****"
