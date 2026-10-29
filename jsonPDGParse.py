import json
import sbcwireless
import guitest
import sys

def parse(handshakeopen):
#This takes care of the initial handshake parsing
    file_data = handshakeopen
    handshake = file_data['Handshake']
    title = file_data['Title']
    guiscale = file_data['SizeofGUI']
#The Options might need more work to dynamically create variables based on how many options are provided
    options = list(file_data['Options'].items())
    option1 = options[0];
#This handles the actual json data packet parsing
    with open("jsonData.json", "r") as data_file:
        data = json.load(data_file)
        deviceID = data['Device_ID']
        checksum1 = data['Checksum']
        timestamp = data['Timestamp']
        address = data['Addresser']
        checksum2 = data['Checksum_2']
        if checksum2 != checksum1:
            sys.exit("Checksum Failed, Data May Be Corrupted")
        dataType = data['Type']
        senderID = None
        message = None
        dataparse1 = None
        dataparse2 = None
        dataparse3 = None
        dataparse4 = None
        floatval1 = None
        floatval2 = None
        floatval3 = None
#If the datatype specified in the initial packet is of a message
    if dataType == "Message":
        messagedata = list(data['messages'].values())
        senderID = messagedata[0]
        message = messagedata[1]
#If datatype is specified to be Word
    if dataType == "Word":
        devicedata = list(data['word'].values())
        dataparse1 = devicedata[0]
        dataparse2 = devicedata[1]
        dataparse3 = devicedata[2]
        dataparse4 = devicedata[3]
#If datatype is specified to be Float
    if dataType == "Float":
        devicefloat = list(data['float'].values())
        floatval1 = devicefloat[0]
        floatval2 = devicefloat[1]
        floatval3 = devicefloat[2]
    guitest.receivefromparse(options,senderID,message,dataparse1,dataparse2,dataparse3,dataparse4,floatval1,floatval2,floatval3,title,guiscale)
