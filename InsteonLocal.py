#from urllib import urlencode
import requests, time, pprint, logging, logging.handlers, sys, json
from collections import OrderedDict

# todo
# move switch to its own class?
# error handling
# buffer handling - handle broadcasts?
# device list
# linking
# scenes
# sprinkler
# pool
# leak detector
# thermostats
# sensor open/close
# sensor hidden door
# sensor motion
# sensor leak (leak detector)
# smoke bridge
# io module
# ceiling fan
# micro dimmer
# on/off micro
# open/close micro
# ballast dimmer
# dimmer in-line
# mini remote
# outlets
# garage controller
# other devices
# allow setting operating flags (program lock, led off, beeper off)

class InsteonLocal(object):

    def __init__(self, ip, username, password, port="25105", logfile="/tmp/insteonlocal.log", consoleLog = False):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port

        json_cats = open('device_categories.json')
        json_cats_str = json_cats.read()
        self.deviceCategories = json.loads(json_cats_str)

        json_models = open('device_models.json')
        json_models_str = json_models.read()
        self.deviceModels = json.loads(json_models_str)

        self.hubUrl = 'http://' + self.ip + ':' + self.port

        # Standard command (not extended)
        self.StdFlag = "0F"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(logfile, mode='a')
        fh.setLevel(logging.INFO)

        formatter = logging.Formatter('[%(asctime)s] ' +
                     '(%(filename)s:%(lineno)s) %(message)s',
    				datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

        if (consoleLog):
            ch = logging.StreamHandler(stream=sys.stdout)
            ch.setLevel(logging.INFO)
            self.logger.addHandler(ch)


    ## Convert numeric brightness percentage into hex for insteon
    def brightnessToHex(self, level):
        levelInt = int(level)
        newInt = int((levelInt * 255)/100)
        newLevel = format(newInt, '02X')
        self.logger.debug("brightnessToHex: {} to {}".format(level, str(newLevel)))
        return str(newLevel)


    ## Send raw command via post
    def postDirectCommand(self, commandUrl):
        self.logger.info("postDirectCommand: {}".format(commandUrl))
        return requests.post(commandUrl,
            auth=requests.auth.HTTPBasicAuth(self.username, self.password))


    ## Send raw comment via get
    def getDirectCommand(self, commandUrl):
        self.logger.info("getDirectCommand: {}".format(commandUrl))
        return requests.get(commandUrl,
            auth=requests.auth.HTTPBasicAuth(self.username, self.password))


    # Wrapper to send posted direct command and get response
    # level 0 to 100
    def directCommand(self, deviceId, command, level):
        self.logger.info("directCommand: Device {} Command {} Level {}".format(deviceId, command, level))
        deviceId = deviceId.upper()
        levelHex = self.brightnessToHex(level)
        commandUrl = (self.hubUrl + '/3?' + "0262"
                    + deviceId + self.StdFlag
                    + command + levelHex + "=I=3")
        return self.postDirectCommand(commandUrl)


    # Wrapper to send posted scene command and get response
    def sceneCommand(self, groupNum, command):
        self.logger.info("sceneCommand: Group {} Command {}".format(groupNum, command))
 #       levelHex = self.brightnessToHex(level)
        commandUrl = self.hubUrl + '/0?' + command + groupNum + "=I=0"
        return self.postDirectCommand(commandUrl)


    # Direct hub command
    def directCommandHub(self, command):
        self.logger.info("directCommandHub: Command {}".format(command))
        commandUrl = (self.hubUrl + '/3?' + command + "=I=3")
        return self.postDirectCommand(commandUrl)


    # Wrapper for short-form commands (doesn't need device id or flags byte)
    # For group commands
    def directCommandShort(self, command):
        self.logger.info("directCommandShort: Command {}".format(command))
        commandUrl = (self.hubUrl + '/3?' + command + "=I=0")
        return self.postDirectCommand(commandUrl)


    # Get a list of all currently linked devices
    def getLinked(self):
        linkedDevices = {}
        self.logger.info("\ngetLinked")

        #todo instead of sleep, create loop to keep checking buffer
        self.directCommandHub("0269")
        time.sleep(1)
        status = self.getBufferStatus()
        if (status['linkedDev'] == "000000"):
            self.logger.info("getLinked: No devices linked")
            return linkedDevices

        devCat = self.getDeviceCategory(status['linkedDevCat'])
        if "name" in devCat:
            devCatName = devCat["name"]
            devCatType = devCat["type"]
        else:
            devCatName = "Unknown"
            devCatType = "unknown"
        linkedDevModel = self.getDeviceModel(status["linkedDevCat"], status["linkedDevSubcat"])
        if "name" in linkedDevModel:
            devModelName = linkedDevModel["name"]
        else:
            devModelName = "unknown"
        self.logger.info("getLinked: Got first device: {} group {} cat type {} cat name {} dev model name {}".format(status['linkedDev'], status['linkedGroupNum'], devCatType, devCatName, devModelName))
        linkedDevices[status['linkedGroupNum']] = status['linkedDev']

        while (status['success']):
            self.directCommandHub("026A")
            time.sleep(1)
            status = self.getBufferStatus()
            if (status['linkedDev'] != "000000"):
                devCat = self.getDeviceCategory(status['linkedDevCat'])
                if "name" in devCat:
                    devCatName = devCat["name"]
                    devCatType = devCat["type"]
                else:
                    devCatName = "Unknown"
                    devCatType = "unknown"
                linkedDevModel = self.getDeviceModel(status["linkedDevCat"], status["linkedDevSubcat"])
                if "name" in linkedDevModel:
                    devModelName = linkedDevModel["name"]
                else:
                    devModelName = "unknown"
                self.logger.info("getLinked: Got |device| {} |group| {} |cat type| {} |cat name| {} |dev model name| {}".format(status['linkedDev'], status['linkedGroupNum'], devCatType, devCatName, devModelName))
                linkedDevices[status['linkedGroupNum']] = status['linkedDev']

        self.logger.info("getLinked: Final device list: {}".format(pprint.pformat(linkedDevices)))
        return linkedDevices


    # Given the category id, return name and type for the caegory
    def getDeviceCategory(self, cat):
        if cat in self.deviceCategories:
            return self.deviceCategories[cat]
        else:
            return false


    # Return the model name given cat/subcat or product key
    def getDeviceModel(self, cat, subCat, key=''):
        if cat + ":" + subCat in self.deviceModels:
            return self.deviceCategories[cat]
        else:
            for k,v in self.deviceModels.items():
                if "key" in v:
                    if v["key"] == key:
                        return v
            return false


    # Get the device for the ID. ID request can return device type (cat/subcat), firmware ver, etc.
    # cat is status['response2Cat'], sub cat is status['response2Subcat']
    def idRequest(self, deviceId):
        self.logger.info("\nidRequest for device {}".format(deviceId))
        deviceId = deviceId.upper()

        self.directCommand(deviceId, "10", "00")

        time.sleep(2)

        status = self.getBufferStatus()

        return status

    # Do a separate query to get device status. This can tell if device is on/off, lighting level, etc.
    # status['responseCmd2'] is lighting level
    def getDeviceStatus(self, deviceId):
        self.logger.info("\ngetDeviceStatus for device {}".format(deviceId))
        deviceId = deviceId.upper()

        self.directCommand(deviceId, "19", "00")

        time.sleep(2)

        status = self.getBufferStatus()

        return status


    # Main method to read from buffer
    def getBufferStatus(self):
        commandUrl = self.hubUrl + '/buffstatus.xml'
        self.logger.info("getBufferStatus: {}".format(commandUrl))

        response = self.getDirectCommand(commandUrl)
        responseText = response.text
        responseText = responseText.replace('<response><BS>', '')
        responseText = responseText.replace('</BS></response>', '')

        responseStatus = OrderedDict()

        responseType = responseText[0:4]

        self.logger.info("getBufferStatus: Got Response type {} text of {}".format(responseType, responseText))

        if (responseType == '0250'):
            # TODO
            self.logger.err("Not implemented handling 0250 standard message")
        elif (responseType == '0251'):
            # TODO
            self.logger.err("Not implemented handling 0251 extended message")
        elif (responseType == '0252'):
            self.logger.err("Not implemented handling 0252 X10 message received")
        elif (responseType == '0253'):
            # TODO
            self.logger.err("Not implemented handling 0251 extended message")
        elif (responseType == '0254'):
            # TODO
            self.logger.err("Not implemented handling 0254 Button Event Report")
            # next byte:
            # 2 set button tapped
            # 3 set button held
            # 4 set button released after hold
            # 12 button 2 tapped
            # 13 button 2 held
            # 14 button 2 released after hold
            # 22 button 3 tapped
            # 23 button 3 held
            # 24 button 3 released after hold
        elif (responseType == '0255'):
            # TODO
            self.logger.err("Not implemented handling 0255 User Reset - user pushed and held SET button on power up")
        elif (responseType == '0256'):
            # TODO
            self.logger.err("Not implemented handling 0256 All-link cleanup failure")
        elif (responseType == '0257'):
            # TODO
            self.logger.err("Not implemented handling 0257 All-link record response")
        elif (responseType == '0258'):
            # TODO
            self.logger.err("Not implemented handling 0258 All-link cleanup status report")
        elif (responseType == '0259'):
            # TODO
            self.logger.err("Not implemented handling 0259 database record found")
        elif (responseType == '0261'):
            # scene response
            self.logger.info("Response type 0261 scene response")
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['sendCmdType']      = responseText[0:4]
            responseStatus['groupNum']         = responseText[4:6]
            responseStatus['groupCmd']         = responseText[6:8] # 11 for on
            responseStatus['groupCmdArg']      = responseText[8:10] # ????
            responseStatus['ackorNak']         = responseText[10:12]

        elif (responseType == '0262'):
            self.logger.info("Response type 0262")
            # Pass through command to PLM
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['sendCmdType']      = responseText[0:4] # direct vs scene,
            responseStatus['sendDevice']       = responseText[4:10]
            responseStatus['sendCmdFlag']      = responseText[10:12] # std vs extended
            responseStatus['sendCmd']          = responseText[12:14]
            responseStatus['sendCmdArg']       = responseText[14:16]
            responseStatus['ackorNak']         = responseText[16:18] # 06 ok 15 error
            responseStatus['responseCmdStart'] = responseText[18:20]
            responseStatus['responseType']     = responseText[20:22]
            responseStatus['responseDevice']   = responseText[22:28]
            responseStatus['responseHub']      = responseText[28:34]
            responseStatus['responseFlag']     = responseText[34:35] # 2 for ack
            responseStatus['responseHopCt']    = responseText[35:36] # hop count F, B, 7, or 3
            responseStatus['responseCmd1']     = responseText[36:38] # database delta
            responseStatus['responseCmd2']     = responseText[38:40] # brightness, etc.

            if ((len(responseText) > 40) and (responseText[40:44] != "0000") and (responseText[0:44] != "")):
                # we have another message - like id response
                responseStatus['response2Type']     = responseText[40:44]
                responseStatus['response2Device']   = responseText[44:50]
                responseStatus['response2Cat']      = responseText[50:52]
                responseStatus['response2Subcat']   = responseText[52:54]
                responseStatus['response2Firmware'] = responseText[54:56]
                responseStatus['response2Flag']     = responseText[56:57]
                responseStatus['response2HopCt']    = responseText[57:58]
                responseStatus['response2Cmd1']     = responseText[58:60]
                responseStatus['responseCmd2']      = responseText[60:62]

        elif ((responseType == '0269') or (responseType == '026A')):
            # Response from getting devices from hub
            responseStatus['error']            = True
            responseStatus['success']          = False
            responseStatus['message']          = ''
            responseStatus['sendCmd']          = responseText[0:4] # 0269
            responseStatus['ackorNak']         = responseText[4:6] # 06 ack 15 nak or empty
            responseStatus['responseCmd']      = responseText[6:10] # 0257 all link record response
            responseStatus['responseFlags']    = responseText[10:12] # 00-FF is controller...bitted for in use, master/slave, etc. See p44 of INSTEON Hub Developers Guide 20130618
            responseStatus['linkedGroupNum']   = responseText[12:14]
            responseStatus['linkedDev']        = responseText[14:20]
            responseStatus['linkedDevCat']     = responseText[20:22] # 01 dimmer
            responseStatus['linkedDevSubcat']  = responseText[22:24] # varies by device type
            responseStatus['linkedDevFirmVer'] = responseText[24:26] # varies by device type

        pprint.pprint(responseStatus)
        if ((not responseText) or (responseText == 0) or (responseType == "0000")):
            responseStatus['error'] = True
            responseStatus['success'] = False
            responseStatus['message'] = 'Empty buffer'
        elif (responseStatus['ackorNak'] == '06'):
            responseStatus['success'] = True
            responseStatus['error'] = False
        elif (responseStatus['ackorNak'] == '15'):
            responseStatus['success'] = False
            responseStatus['error'] = True
            responseStatus['message'] = 'Device returned nak'

        self.logger.info("getBufferStatus: Received response of: {}".format(pprint.pformat(responseStatus)))

        # Best to clear it after reading it. It overwrites the buffer left
        # to right but doesn't clear out old chars past what it wrote. Last
        # two bytes tell where it stopped writing
        self.clearBuffer()
        return responseStatus


    ## Check if last command succeeded  by checking buffer
    def checkSuccess(self, deviceId, level):
        deviceId = deviceId.upper()

        self.logger.info('checkSuccess: for device {} level {}'.format(deviceId, level))

        time.sleep(2)
        status = self.getBufferStatus()
        statusDevice = status.get("responseDevice", "")
        statusCmdArg = status.get("responseCmd2", "")
        statusSuccess = status.get("success", False)
        self.logger.info('checkSuccess: Got status {}'.format(pprint.pformat(status)))
        self.logger.info('checkSuccess: Response device {} cmd {}'.format(statusDevice, statusCmdArg))
        if ((statusDevice == deviceId) and statusSuccess
            and (statusCmdArg == self.brightnessToHex(level))):
            self.logger.info('checkSuccess: Switch command was successful')
            return True
        else:
            self.logger.error('checkSuccess: Switch command failed')
            self.logger.info('checkSuccess: Device compare {} to {}'.format(deviceId, statusDevice))
            self.logger.info('checkSuccess: Level compare {} to {}'.format(self.brightnessToHex(level), statusCmdArg))
            return False


    ## Clear the hub buffer
    def clearBuffer(self):
        commandUrl = self.hubUrl + '/1?XB=M=1'
        response = self.postDirectCommand(commandUrl)
        self.logger.info("clearBuffer: {}".format(response))
        return response



### TODO listen for linked page 35 http://cache.insteon.com/developer/2242-222dev-062013-en.pdf

   ### Group Commands

    # Enter linking mode for a group
    def enterLinkMode(self, groupNumber):
        self.logger.info("\nenterLinkMode for group {}".format(groupNumber));
        self.directCommandShort('09' + groupNumber)
        # should send http://0.0.0.0/0?0901=I=0

        ## TODO check return status
        status = self.getBufferStatus()
        return status


    # Enter unlinking mode for a group
    def enterUnlinkMode(self, groupNumber):
        self.logger.info("\nenterUnlinkMode for group {}".format(groupNumber));
        self.directCommandShort('0A' + groupNumber)
        # should send http://0.0.0.0/0?0A01=I=0

        ## TODO check return status
        status = self.getBufferStatus()
        return status


    # Cancel linking or unlinking mode
    def cancelLinkUnlinkMode(self):
        self.logger.info("\ncancelLinkUnlinkMode");
        self.directCommandShort('08')
        # should send http://0.0.0.0/0?08=I=0

        ## TODO check return status
        status = self.getBufferStatus()
        return status



    ## Begin all linking
    # linkType:
    #  00 as responder/slave
    #  01 as controller/master
    #  03 as controller with im initiates all linking or as responder when another device initiates all linking
    #  FF deletes the all link
    def startAllLinking(self, linkType):
        self.logger.info("\nstartAllLinking for type " + linkType)
        self.directCommandHub('0264' + linkType)
    # TODO: read response
#    Byte Value Meaning
#1 0x02 Echoed Start of IM Command
#2 0x64 Echoed IM Command Number
#3 <Code> Echoed <Code>
#4 <ALL-Link Group> Echoed <ALL-Link Group>
#5 <ACK/NAK> 0x06 (ACK) if the IM executed the Command correctly
#0x15 (NAK) if an error occurred


    def cancelAllLinking(self):
        self.logger.info("\ncancelAllLinking")
        self.directCommandHub('0265')
## TODO read response
    # 0x02 echoed start of command
    # 0x65 echoed im command
    # ack 06 or nak 15


    ### Group Lighting Functions - note, groups cannot be dimmed. They can be linked in dimmed mode.

    # Turn group on
    def groupOn(self, groupNum):
        self.logger.info("\ngroupOn: group {}".format(groupNum))
        self.sceneCommand(groupNum, "11")

        time.sleep(2)
        status = self.getBufferStatus()

        #success = self.checkSuccess(deviceId, level)
        ### Todo - probably can't check this way, need to do a clean up and check status of each one, etc.
        #if (success):
        #    self.logger.info("groupOn: Group turned on successfully")
        #else:
        #    self.logger.error("groupOn: Group did not turn on")


    # Turn group off
    def groupOff(self, groupNum):
        self.logger.info("\ngroupOff: group {}".format(groupNum))
        self.sceneCommand(groupNum, "13")

        time.sleep(2)
        status = self.getBufferStatus()
        #success = self.checkSuccess(deviceId, level)
        ### Todo - probably can't check this way, need to do a clean up and check status of each one, etc.
        #if (success):
        #    self.logger.info("groupOff: Group turned off successfully")
        #else:
        #    self.logger.error("groupOff: Group did not turn off")



    ### Lighting Functions


    ## Turn light On
    # fast seems to always do full brightness
    def lightOn(self, deviceId, level, fast=0):
        deviceId = deviceId.upper()

        self.logger.info("\nlightOn: device {} level {} fast {}".format(deviceId, level, fast))

        if fast:
            self.directCommand(deviceId, "12", level)
        else:
            self.directCommand(deviceId, "11", level)

        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightOn: Light turned on successfully")
        else:
            self.logger.error("lightOn: Light did not turn on")


    ## Turn Light Off
    # doesn't seem to be a speed difference with fast
    def lightOff(self, deviceId, fast=0):
        deviceId = deviceId.upper()

        self.logger.info("\nlightOff: device {} fast {}".format(deviceId, fast))

        if fast:
            self.directCommand(deviceId, "14", '00')
        else:
            self.directCommand(deviceId, "13", '00')

        success = self.checkSuccess(deviceId, '00')
        if (success):
            self.logger.info("lightOff: Light turned off successfully")
        else:
            self.logger.error("lightOff: Light did not turn off")



    ## Change light level
    def lightLevel(self, deviceId, level):
        deviceId = deviceId.upper()

        self.logger.info("\nlightLevel: device {} level {}".format(deviceId, level))

        self.directCommand(deviceId, "21", level)
        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightLevel: Light level changed successfully")
        else:
            self.logger.error("lightLevel: Light level was not changed")



    ## Brighten light by one step
    def lightBrightenStep(self, deviceId):
        deviceId = deviceId.upper()

        self.logger.info("\nlightBrightenStep: device{}".format(deviceId))

        self.directCommand(deviceId, "15", "00")
        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightBrightenStep: Light brightened successfully")
        else:
            self.logger.error("lightBrightenStep: Light brightened failure")


    ## Dim light by one step
    def lightDimStep(self, deviceId):
        deviceId = deviceId.upper()

        self.logger.info("\nlightDimStep: device{}".format(deviceId))

        self.directCommand(deviceId, "16", "00")
        success = self.checkSuccess(deviceId, level)
        if (success):
            self.logger.info("lightDimStep: Light dimmed successfully")
        else:
            self.logger.error("lightDimStep: Light dim failure")
