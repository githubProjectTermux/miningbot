import sys
import time
import telepot
import requests
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

#define markup Dictionary for edit of messages
markupDict = {}
#define username dictionary
userNameDict = {}


#check if Rig is up
def checkRigUpStatus():
    '''for key, values in userNameDict.items():
        #print(key, values) #debugging
        getRigServerData(key, [values, 1], True)'''

def getRigServerData(chat_id, markupReturnData, closeList):
    markup_contents = []
    markup_contents_2ndHalf = []
    minerUpStatus = ["empty"]
    count = 1
    message_server = ""

    while 1:
        try:
            #send stats of rig to cilent
            aFile = open(userNameDict[chat_id] + "_" + str(count) + "_" + "statsServer.txt")

            #read stats of the selected miner
            allDetails = aFile.readlines()

            #if file time difference is less than 5mins(300sec), means it's still up (using epoch as time)
            if abs(int(time.time()) - int(allDetails[0])) < 300:
                #blue circle picture
                minerUpStatus.append("🔵")
            else:
                #red circle picture
                minerUpStatus.append("🔴")

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
            print(ex, "exception when reading file")

        else:
            #clear it each markup must have text so example mine2 markup will send miner1's stats as text
            message_server = ""

            #No. GPUs
            allDetails[46] = allDetails[46].split()
            message_server += "\nNo. of GPUs = " + allDetails[46][1]

            #Temp
            allDetails[31] = allDetails[31].split()
            message_server += "\nTemp = " + allDetails[31][1] + "degrees\n"

            #Status
            allDetails[43] = allDetails[43].split()
            message_server += "\nMining Status = " + allDetails[43][3] + " " + allDetails[43][4]

            #Hash rate
            allDetails[49] = allDetails[49].split()
            message_server += "\nHash rate = " + allDetails[49][1]


            #pop out from RAM to save RAM space since no longer inused
            aFile.close()

        count += 1


    #create buttons of miner1 to the miner number that user selected to see the stats
    #condition assignment is used so that it won't stop at int(markupReturnData[1]) if closeList is True
    for i in range(1, count if closeList else int(markupReturnData[1])+1):
        markup_contents.append([InlineKeyboardButton(text="miner" + str(i) + " " + str(minerUpStatus[i]), callback_data=markupReturnData[0] + "_" + str(i))])
        
        if i == int(markupReturnData[1]):
            if not closeList:
                if len(markup_contents) != 0:
                    markup_contents.pop()
                markup_contents.append([InlineKeyboardButton(text="miner" + str(i) + " " + str(minerUpStatus[i]), callback_data=markupReturnData[0] + "+" + str(i))])
    
    for i in range(int(markupReturnData[1])+1, count):

        markup_contents_2ndHalf.append([InlineKeyboardButton(text="miner" + str(i) + " " + str(minerUpStatus[i]), callback_data=markupReturnData[0] + "_" + str(i))])


    #create Markup from 
    minerInfoButtons = InlineKeyboardMarkup(inline_keyboard=markup_contents)

    #useful when server restarted and user clicked on previous inLine buttons
    try:
        print(markupReturnData)
        markupDict[chat_id] = bot.editMessageText(telepot.message_identifier(markupDict[chat_id]), text=markupReturnData[0] + " status", reply_markup=minerInfoButtons)
    except Exception as ex:
        print(ex, "editMessage failed")
        markupDict[chat_id] = bot.sendMessage(chat_id, text=markupReturnData[0] + " status", reply_markup=minerInfoButtons)

    minerInfoButtons = InlineKeyboardMarkup(inline_keyboard=markup_contents_2ndHalf)


    #Don't send it there are no 2nd half of the buttons after the drop down list
    if len(message_server) != 0:
        #useful when server restarted and user clicked on previous inLine buttons
        #markupDict[str(chat_id)+str("_1")] instead of markupDict[chat_id] as is to store identifier of 2nd half of the message/buttons
        try:
            markupDict[str(chat_id)+str("_1")] = bot.editMessageText(telepot.message_identifier(markupDict[str(chat_id)+str("_1")]), text=message_server, reply_markup=minerInfoButtons)
        except:
            markupDict[str(chat_id)+str("_1")] = bot.sendMessage(chat_id, text=message_server, reply_markup=minerInfoButtons)
    else:
        #try to delete dropdownlist if user selected to close it
        try:
            bot.deleteMessage(telepot.message_identifier(markupDict[str(chat_id)+str("_1")]))
        except:
            pass

#handles commands
def handle_commands(chat_id, commands, message_cilent):
    message_cilent_list = []
    #will only print miner numbers but not contents(stats of the miners)
    if commands == "start":
        #store user's username which link to chat id for future use
        userNameDict[chat_id] = message_cilent

        #convert message into list as the function parameter to use is in list
        message_cilent_list.append(message_cilent)
        message_cilent_list.append("1")

        getRigServerData(chat_id, message_cilent_list, True)


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

        #get currency exchange rate from http://www.mas.gov.sg/Statistics/APIs/API-Documentation.aspx
        r = requests.get("https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id=95932927-c8bc-4e7a-b484-68a66a24edfe&filters[end_of_day]=" + time.strftime("%Y-%m-%d"))
        currency_converter = r.json()

        #sending data from nanopool to user
        bot.sendMessage(chat_id, text="[Current]" + \
            "\nHashrate: " + nanopool_data['data']['hashrate'] + "H/s" + \
            "\nUSD: $" + str(currentEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd']) * (currentEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\n[Average for last 1 hour]" + \
            "\nHashrate: " + nanopool_data['data']['avgHashrate']['h1'] + "H/s" + \
            "\nUSD: $" + str(avg1hourEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd']) * (avg1hourEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\n[Average for last 6 hours]" + \
            "\nHashrate: " + nanopool_data['data']['avgHashrate']['h6'] + "H/s" + \
            "\nUSD: $" + str(avg6hourEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd']) * (avg6hourEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\n[Average for last 24 hours]" + \
            "\nHashrate: " + nanopool_data['data']['avgHashrate']['h24'] + "H/s" + \
            "\nUSD: $" + str(avg12hourEarning['data']['month']['dollars']) + "/month" + \
            "\nSGD: $" + str((float(currency_converter['result']['records'][0]['usd_sgd']) * (avg12hourEarning['data']['month']['dollars']) * 10**12 )/10**12) + "/month" + \
            "\n" + \
            "\nBalance: " + nanopool_data['data']['balance'] + "ETN" + \
            "\nUnconfirmed Balance: " + nanopool_data['data']['unconfirmed_balance'] + "ETN")


#handles messages sent from inline keyboards
def handle_inlinekeyboard(msg): 
    #print(msg) #debug
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    #incase used in 
    chat_id = msg['message']['chat']['id']
    #remember markup returns <username>_<miner no.>? So split them now
    markupReturnData = msg['data'].split("_")
    closeList = False

    if len(markupReturnData) == 1:
        markupReturnData = msg['data'].split("+")
        #set close list to TRUE
        closeList = True


    getRigServerData(chat_id, markupReturnData, closeList)


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
        if len(query_message) == 2:
            handle_commands(chat_id, query_message[0], query_message[1])
        else:
            bot.sendMessage(chat_id, "Input either: \n/start <username> \nor \n/report <picture or message of bugs>")

        return


bot = telepot.Bot("432196079:AAGRT5Ym2dm1h8fWq9b6RUfWdEkWQc2ra9c")

MessageLoop(bot, {'chat': handle, 'callback_query': handle_inlinekeyboard}).run_as_thread()
print("listening...")

while 1:
    time.sleep(30)
    checkRigUpStatus()
