## miningInfoBot Telegram Bot version 1.0 ##

import sys
import time
import telepot
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, timedelta

#define markup Dictionary for edit of messages
markupDict = {}
#define minerUpStatus
minerUpStatus = {}
#define username dictionary
userNameDict = {}


#check if Rig is up
def checkRigUpStatus():
    #for comparison if there are changes in status
    minerUpStatus_check = {}
    count = 1
    dicts = "data/"

    for chat_id, username in userNameDict.items():
        #minerUpStatus[chat_id][0] is ["empty"] so must set the same
        minerUpStatus_check[chat_id] = ["empty"]
        count = 1

        while 1:
            try:
                #send stats of rig to cilent
                aFile = open(dicts + username + "_" + str(count) + "_" + "statsServer.txt")

                #read stats of the selected miner
                allDetails = aFile.readlines()

                #if file time difference is less than 5mins(300sec), means it's still up (using epoch as time)
                if abs(int(time.time()) - int(allDetails[0])) < 300:
                    #blue circle picture
                    minerUpStatus_check[chat_id].append("🔵")
                else:
                    #red circle picture
                    minerUpStatus_check[chat_id].append("🔴")
            except IOError:
                #exit while loop to stop checking
                break

            except Exception as ex:
                print(ex)   #debugging

                #pop out from RAM to save RAM space since no longer inused
                aFile.close()

                break

            else:
                #pop out from RAM to save RAM space since no longer inused
                aFile.close()

            count += 1

        if (len(minerUpStatus[chat_id]) == len(minerUpStatus_check[chat_id])) and (minerUpStatus[chat_id] == minerUpStatus_check[chat_id]):
            continue
        else:
            #send customer an updated info
            handle_commands(chat_id, "start", username)



#handles commands
def handle_commands(chat_id, commands, message_cilent):
    markup_contents = []
    count = 1
    dicts = "data/"
    dicts_bugs = "issues/"

    #will only print miner numbers but not contents(stats of the miners)
    if commands == "start":
        #store user's username which link to chat id for future use
        userNameDict[chat_id] = message_cilent
        #reset minerUpStatus content
        minerUpStatus[chat_id] = ["empty"]

        while 1:
            try:
                #send stats of rig to cilent
                aFile = open(dicts + message_cilent + "_" + str(count) + "_" + "statsServer.txt")

                #read stats of the selected miner
                allDetails = aFile.readlines()

                #if file time difference is less than 5mins(300sec), means it's still up (using epoch as time)
                if abs(int(time.time()) - int(allDetails[0])) < 300:
                    #blue circle picture
                    minerUpStatus[chat_id].append("🔵")
                else:
                    #red circle picture
                    minerUpStatus[chat_id].append("🔴")

            #exception thrown if file doesn't exist
            except IOError:
                break

            except Exception as ex:
                print(ex)   #debugging

                #pop out from RAM to save RAM space since no longer in used
                aFile.close()

                break

            else:
                #return <username>_<miner no.>
                markup_contents.append([InlineKeyboardButton(text="miner" + str(count) + " " + str(minerUpStatus[chat_id][count]), callback_data=message_cilent + "_" + str(count))])

                #pop out from RAM to save RAM space since no longer inused
                aFile.close()

            count += 1

        
        #create Markup from 
        minerInfoButtons = InlineKeyboardMarkup(inline_keyboard=markup_contents)

        #for future edit or delete of message
        markupDict[chat_id] = bot.sendMessage(chat_id, text=message_cilent + " status", reply_markup=minerInfoButtons)


    #web scrapping from https://etn.nanopool.org/api
    if commands == "all":
        #message_cilent will contain the wallet address
        #get general wallet info
        r = requests.get("https://api.nanopool.org/v1/etn/user/" + message_cilent)
        #print(r.json())    #debug
        nanopool_data = r.json()

        #get earning by hash rate from https://etn.nanopool.org/api
        r = requests.get("https://api.nanopool.org/v1/etn/approximated_earnings/" + nanopool_data['data']['hashrate'])
        currentEarning = r.json()
        r = requests.get("https://api.nanopool.org/v1/etn/approximated_earnings/" + nanopool_data['data']['avgHashrate']['h1'])
        avg1hourEarning = r.json()
        r = requests.get("https://api.nanopool.org/v1/etn/approximated_earnings/" + nanopool_data['data']['avgHashrate']['h6'])
        avg6hourEarning = r.json()
        r = requests.get("https://api.nanopool.org/v1/etn/approximated_earnings/" + nanopool_data['data']['avgHashrate']['h12'])
        avg12hourEarning = r.json()

        #get today's End Of Day currency exchange rate from http://www.mas.gov.sg/Statistics/APIs/API-Documentation.aspx
        r = requests.get("https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id=95932927-c8bc-4e7a-b484-68a66a24edfe&filters[end_of_day]=" + time.strftime("%Y-%m-%d"))
        currency_converter = r.json()
        

        #Incase Nanopool is down as it's frequency down
        if nanopool_data['status'] == False:
            bot.sendMessage(chat_id, "Nanopool is current down.")
            return

        #Incase MAS is down as it's frequency down
        if currency_converter['success'] == False:
            #get yesterday's date
            yesterday = date.today() - timedelta(1)

            #get yesterday's End Of Day currency exchange rate from http://www.mas.gov.sg/Statistics/APIs/API-Documentation.aspx
            r = requests.get("https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id=95932927-c8bc-4e7a-b484-68a66a24edfe&filters[end_of_day]=" + yesterday.strftime("%Y-%m-%d"))
            currency_converter = r.json()

            if currency_converter['success'] == False:
                bot.sendMessage(chat_id, "Currency converter is current down. Only USD is available.")

        #sending data from nanopool to user
        bot.sendMessage(chat_id, text="[Current]" + \
            "\nHashrate: " + nanopool_data['data']['hashrate'] + "H/s" + \
            "\nUSD: $" + str(currentEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd'] if currency_converter['success'] == True else 0.0) * (currentEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\n[Average for last 1 hour]" + \
            "\nHashrate: " + nanopool_data['data']['avgHashrate']['h1'] + "H/s" + \
            "\nUSD: $" + str(avg1hourEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd'] if currency_converter['success'] == True else 0.0) * (avg1hourEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\n[Average for last 6 hours]" + \
            "\nHashrate: " + nanopool_data['data']['avgHashrate']['h6'] + "H/s" + \
            "\nUSD: $" + str(avg6hourEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd'] if currency_converter['success'] == True else 0.0) * (avg6hourEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\n[Average for last 24 hours]" + \
            "\nHashrate: " + nanopool_data['data']['avgHashrate']['h24'] + "H/s" + \
            "\nUSD: $" + str(avg12hourEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd'] if currency_converter['success'] == True else 0.0) * (avg12hourEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\nBalance: " + nanopool_data['data']['balance'] + "ETN" + \
            "\nUnconfirmed Balance: " + nanopool_data['data']['unconfirmed_balance'] + "ETN")


    #for admin to send to all user as announcement
    if commands == "Leon_HaoJie_SendToAll":
        for chat_ids in userNameDict:
            bot.sendMessage(chat_ids, message_cilent)


    #log bugs sent by customers
    if commands == "report":
        #write to bug reporting text file
        aFile = open(dicts_bugs + str(chat_id) + "_reportbugs.txt", "a")
        aFile.write(time.strftime("[%d/%m/%Y %H:%M:%S] ") + message_cilent + "\n\n")

        #pop from RAM
        aFile.close()


#handles messages sent from markup keyboards
def handle_markupkeyboard(msg): 
    #print(msg) #debug
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    #incase used in group chat
    chat_id = msg['message']['chat']['id']
    #remember markup returns <username>_<miner no.>? So split them now
    markupReturnData = msg['data'].split("_")
    markup_contents = []
    markup_contents_2ndHalf = []
    minerUpStatus[chat_id] = ["empty"]
    count = 1
    message_server = ""
    closeList = False
    dicts = "data/"


    if len(markupReturnData) == 1:
        markupReturnData = msg['data'].split("+")
        #set close list to TRUE
        closeList = True


    while 1:
        try:
            #send stats of rig to cilent
            aFile = open(dicts + userNameDict[chat_id] + "_" + str(count) + "_" + "statsServer.txt")

            #read stats of the selected miner
            allDetails = aFile.readlines()

            #if file time difference is less than 5mins(300sec), means it's still up (using epoch as time)
            if abs(int(time.time()) - int(allDetails[0])) < 300:
                #blue circle picture
                minerUpStatus[chat_id].append("🔵")
            else:
                #red circle picture
                minerUpStatus[chat_id].append("🔴")

            # only read stats of the miner selected by the user
            if str(count) != markupReturnData[1] or closeList:
                aFile.close()
                count += 1
                continue


        #if file does not exist
        except IOError:
            #exception thrown if file doesn't exist
            break

        #if cannot find username in dict (RAM's database)
        except KeyError:
            bot.sendMessage(chat_id, "Error searching for username. \nPlease input \n/start <username> \nagain.")
            return

        except Exception as ex:
            print(ex)
            break

        else:
            #code effiency to reduce doing through the codes before if miner is down
            if minerUpStatus[chat_id][count] == "🔴":
                message_server = "Miner down ❌"
                message_server += "\nMaintainance maybe taking place."
                message_server += "\nIf problem persist for 10mins, contact SSIT."

                #pop out from RAM to save RAM space since no longer inused
                aFile.close()
                count += 1

                continue

            #clear it each markup must have text so example mine2 markup will send miner1's stats as text
            message_server = ""
            #print(allDetails)  #debugging

            #No. GPUs
            allDetails[1] = allDetails[1].split()
            message_server += "\nNo. of GPUs = " + allDetails[1][1]

            #Status
            allDetails[2] = allDetails[2].split()
            message_server += "\nMining Status = " + ((" ".join(allDetails[2][1:] + " ❌")) if allDetails[2][1] == "overheat:" else (allDetails[2][3] + " " + allDetails[2][4] + " ✅"))

            message_server += "\n"


            #Temp
            allDetails[3] = allDetails[3].split()

            #Hash rate per GPU
            allDetails[4] = allDetails[4].split()

            #organize it
            for i in range(1, len(allDetails[3][1:]) + 1):
                message_server += "\n[GPU {0}]".format(i) + (" ‼️" if (float(allDetails[4][i]) < 26.0 and float(allDetails[4][i]) > 0.0) else (" ❌" if float(allDetails[4][i]) == 0.0 else ""))

                #Temp
                message_server += "\nTemp = " + allDetails[3][i] + " degrees"

                #Hash rate per GPU
                message_server += "\nHash rates = " + allDetails[4][i]

            message_server += "\n"

            #Total Hash rate
            message_server += "\nTotal hash rate = " + allDetails[2][1] + " " + allDetails[2][2][:-1]


            #pop out from RAM to save RAM space since no longer inused
            aFile.close()

        count += 1


    #create buttons of miner1 to the miner number that user selected to see the stats
    #condition assignment is used so that it won't stop at int(markupReturnData[1]) if closeList is True
    for i in range(1, count if closeList else int(markupReturnData[1])+1):
        markup_contents.append([InlineKeyboardButton(text="miner" + str(i) + " " + str(minerUpStatus[chat_id][i]), callback_data=markupReturnData[0] + "_" + str(i))])
        
        if i == int(markupReturnData[1]):
            if not closeList:
                if len(markup_contents) != 0:
                    markup_contents.pop()
                markup_contents.append([InlineKeyboardButton(text="miner" + str(i) + " " + str(minerUpStatus[chat_id][i]), callback_data=markupReturnData[0] + "+" + str(i))])
    
    for i in range(int(markupReturnData[1])+1, count):

        markup_contents_2ndHalf.append([InlineKeyboardButton(text="miner" + str(i) + " " + str(minerUpStatus[chat_id][i]), callback_data=markupReturnData[0] + "_" + str(i))])


    #create Markup from 
    minerInfoButtons = InlineKeyboardMarkup(inline_keyboard=markup_contents)

    #useful when server restarted and user clicked on previous inLine buttons
    try:
        markupDict[chat_id] = bot.editMessageText(telepot.message_identifier(markupDict[chat_id]), text=markupReturnData[0] + " status", reply_markup=minerInfoButtons)
    except Exception as ex:
        #print(ex)
        markupDict[chat_id] = bot.sendMessage(chat_id, text=markupReturnData[0] + " status", reply_markup=minerInfoButtons)

    minerInfoButtons = InlineKeyboardMarkup(inline_keyboard=markup_contents_2ndHalf)


    #Don't send it there are no 2nd half of the buttons after the drop down list
    if len(message_server) != 0:
        #useful when server restarted and user clicked on previous inLine buttons
        #markupDict[str(chat_id)+str("_1")] instead of markupDict[chat_id] as is to store identifier of 2nd half of the message/buttons
        try:
            markupDict[str(chat_id)+str("_1")] = bot.editMessageText(telepot.message_identifier(markupDict[str(chat_id)+str("_1")]), text=message_server, reply_markup=minerInfoButtons)
        except:
            markupDict[str(chat_id)+str("_1")] = bot.sendMessage(str(chat_id)+str("_1"), text=message_server, reply_markup=minerInfoButtons)
    else:
        #try to delete dropdownlist if user selected to close it
        try:
            bot.deleteMessage(telepot.message_identifier(markupDict[str(chat_id)+str("_1")]))
        except:
            pass


    # answer callback query or else telegram will forever wait on this
    bot.answerCallbackQuery(query_id)


#handles normal message (not sent from inline keyboards)
def handle(msg):
    #print(msg) #debug
    chat_id = msg['chat']['id']
    query_message = msg['text']
    chat_message = ""

    #commands will start with "/"
    if query_message.startswith("/"):
        #remove "/" from user's message
        query_message = query_message[1:].split()

        #incase user sent only commands means length of 1
        if len(query_message) > 1:
            handle_commands(chat_id, query_message[0], " ".join(query_message[1:]))
        else:
            bot.sendMessage(chat_id, "Input either: \n/start <username> \nor \n/all <wallet key> \nor \n/report <reporting bugs>")

        return


bot = telepot.Bot("543465463:AAEP7rB4AedeLL8NRAekzShDhAn-SgZ4xSY")

MessageLoop(bot, {'chat': handle, 'callback_query': handle_markupkeyboard}).run_as_thread()
print("listening...")

while 1:
    time.sleep(120)
    checkRigUpStatus()
