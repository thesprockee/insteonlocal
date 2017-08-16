#!/Users/mlong/hassdev/bin/python3.5
import time,requests,sys
import pprint
from insteonlocal.Hub import Hub
import config
import logging
from sys import stdout

## To begin, create a file called config.py containing:
#host = "hub's ip"
#username = "hub's username"
#password = "hub's password"
# or comment out the import config and manually specify below

try:
    FORMAT = '[%(asctime)s] (%(filename)s:%(lineno)s) %(message)s'
    #logging.basicConfig(format=FORMAT, level=logging.DEBUG, filename='/tmp/insteonlocal.log')
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    logger = logging.getLogger('')

    # create hub object
    hub = Hub(
        config.host,
        config.username, 
        config.password, 
        '25105', #port 
        10, #timeout
        logger
    )
    buffer = hub.get_buffer_status()
except requests.exceptions.RequestException as e:
   if hub.http_code == 401:
       print("Unauthorized...check user/pass for hub\n")
       sys.exit(1)
   else:
       print(e)
       sys.exit(1)

#hub.get_linked()

#insteonLocal.id_request('42902e')

#insteonLocal.get_device_status('42902e')

#modelInfo = insteonLocal.get_device_category("00")
#if ("name" in modelInfo):
#    print("Got name of " + modelInfo["name"])
#pprint.pprint(modelInfo)

# Outlet example
outlet1 = hub.onoffoutlet('444444');
outlet1.bottom_on();
exit

# Dimmer example
#dimmer1 = hub.dimmer('42902e')
#dimmer1.beep()
#dimmer1.on(25)
#dimmer1.status(0)
#dimmer1.status(1)
#dimmer1.brighten_step()
#dimmer1.brighten_step()
#dimmer1.brighten_step()
#dimmer1.brighten_step()
#dimmer1.dim_sS\tep()
#dimmer1.dim_step()
#dimmer1.dim_step()
#dimmer1.change_level(75)
#dimmer1.off_instant()
#dimmer1.on_saved()
#dimmer1.on(75)
#dimmer1.start_change('down')
#time.sleep(1)
#dimmer1.stop_change()
#time.sleep(2)
#dimmer1.on(10)
#dimmer1.start_change('up')
#time.sleep(1)
#dimmer1.stop_change()
#time.sleep(2)
#dimmer1.off_instant()
#time.sleep(1)
#dimmer1.off()

# Get list of linked devices
#devices = hub.get_linked()
#pprint.pprint(devices)

# Group example
#group2 = hub.group("2")
#group2.on()
#time.sleep(1)
#group2.off()

#switch1 = hub.switch('40565b')
#switch1.on()
#switch1.beep()
#switch1.beep()
#switch1.beep()
#switch1.off()
#status = switch1.status()
#pprint.pprint(status)
#switch1.on()
#status = switch1.status()
#print("new status\n")
#pprint.pprint(status)
#switch1.off()

# switch join new group 03 - IN DEVeLOPMENT
#group3 = hub.group("03")
##group3.enter_link_mode()
#hub.start_all_linking("01", group3.groupId) #controller
#switch1 = hub.switch('40565b')
#switch1.start_all_linking("00", group3.groupId) #responder
##    b.direct_command("40565b", "01", group3.groupId)
#time.sleep(2)
#hub.get_buffer_status()
##group3.cancel_link_unlink_mode()

#hub.get_linked()
