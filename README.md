**Steps to compile and run the programs**:
	
	Step 1:
		
		Run the server.py file

		Command to execute the server:
			
			python server.py

	Step 2:
		
		Run the client.py file

		Command to execute the client:
			
			python client.py


	Step 3:
		
		After the client joins the server, it can login/sign to join/create a chat group.

	Step 4:
		
		Multiple client instances can be started for joining/creating different groups.


**Testing**:

	Black-box Testing:
		
		- Covered scenarios like correct input/output.
		- Performance errors for example: only when the user logs in the server then only he will be presented with option of joining or creating a group.
		- Error guessing for example: When the user is presented with option of joining or creating a group then it can only choose/enter those options, any other value will be considered as an invalid entry.
		- Cause-effect graph for example: After being banned from a group a user cannot send/receive any messages to/from that group.

	White-box Testing:
		
		- Statement Coverage for example: When the user is presented with option of joining or creating a group then it can only choose/enter those options, if  any other value is entered then user is presented with "Invalid Entry" message.
		- Branch Coverage for example: If a user tries to join a group from which it is banned then it cannot join that group.


	Testing from user's perspective:
		
		- If a user is not the admin of a group and it tries to kick another user out then it will not be able to do so as this functionality is available only for the admin.
		- Once the user moves out of a group and join some other group then all the messages sent by the user will be received only by the currently joined group and not the previous group.
		- If a user is kicked out of a group then the user can join the group again.
		- The protocol ensures that messages sent by a client in a group is only received by the members of that group.


**Analysis about the robustness of the protocol**:
	
	Implemented all the DFA states of the protocol and was successfully tested multiple times checking each state of the DFA. The implemented protocol satisfies all the protocol requirements. There is room for improvement as it requires error handling in few situations and some more functionalities could be added. The functionalities that have not been implemented in the code have been listed as future work in the extensibility. 

	Example of robustness of the protocol:
		
		- If a user tries to join a group from which it is banned then it cannot join that group.
		- If a user is not the admin of a group and it tries to kick another user out then it will not be able to do so as this functionality is available only for the admin.
		- Once the user moves out of a group and join some other group then all the messages sent by the user will be received only by the currently joined group and not the previous group.
		- If a user is kicked or banned from a group then it cannot send/receive any messages to/from that group.
		- In a group chat "Group 1" if an user A moves out of the chat and creates a new group called "New Group", after this if any other user B of the "Group 1" chat also moves out of the group and wants to join some other group then in the list of available groups "New Group" will be available for user B to join.
		- The creater of the group is made the admin of the group so that there is always an user to execute the admin functionalities. 

	The protocol does not provide any mechanism to handle attacks like fuzzing, DDos attack.


# ChatServiceProtocol
