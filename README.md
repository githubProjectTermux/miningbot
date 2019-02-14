# MiningInfoBot

Hi! This is a Telegram Bot for EthOS Mining OS version 1.2.7. This bot and script helps you to keep track of your mining rig status such as if it is online, the temperature, hash rate, etc. 

I created this bot and script for a company long time ago (December 2017). However, they have stopped using it and allows me to publish my work onto github. This python script takes an older version of EthOS Mining OS (http://ethosdistro.com/). It may no longer work due to new version of the OS and some of the website might no longer exist. However, you can use the code as a reference.

# Files Required

The main files are folder ("data", and "issues"), and others ("miningInfo_RigServer.py", "miningInfoBot_v1.py", "rig_details.txt") to run the whole system. "MiningInfoBot v1.0.doc" is a word document that contains the software you need to download, set, and also explains my code.

# Abtract of each file

miningInfoBot_v1.py is the main python file that bridge between the telegram user and the server.
miningInfo_RigServer.py is a python script that SSH into each of your mining rigs and exact the necessary info so that miningInfoBot_v1.py can send user the data. The data extracted will be stored in the "data" folder. 
rig_details.txt must contain the name of each rig follow by the IP Address of each rig (IP Address of each rig must be static). The username must be in this format, <Name>_<IncrementingNumberFrom1><Space><IPaddress>.

The issues reported by user through the telegram chat to the telegram bot will be stored in "issues" folder.


# Additional Side Note

The rest of the files here are older version or for testing in the past. So you can ignore them or delete them.
