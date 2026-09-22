import json

#This takes care of the initial handshake parsing
with open("jsonHandshake.json", "r") as file:
    file_data = json.load(file)

    handshake = file_data['Handshake']
    title = file_data['Title']
    guiscale = file_data['SizeofGUI']
#The Options might need more work to dynamically create variables based on how many options are provided
options = list(file_data['Options'].values())
option1 = options[0];

#This handles the actual json data packet parsing
with open("jsonData.json", "r") as data_file:
    data = json.load(data_file)
    deviceID = data['Device_ID']
    checksum1 = data['Checksum']
    timestamp = data['Timestamp']
    address = data['Addresser']
    checksum2 = data['Checksum_2']
    dataType = data['Type']

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
