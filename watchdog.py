#! /usr/bin/env python3

import scapy.layers.l2
import requests
import configparser
import os
import logging

# supress self-signed certificate warning 
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

LOGIN = '<API_USER>'
PASSWORD = '<password>'
ADDRESS = '192.168.1.10:5001' #NAS IP and port
ADDRESS_BOOK = {'192.168.1.1' : 'User1', '192.168.1.2' : 'User2'}

dir_path = os.path.dirname(os.path.realpath(__file__)) # get current script dir

# set log dir
if os.path.exists('C:/Windows/'):
    LOG_DIR = dir_path
else:
    LOG_DIR = "/var/log/"

logging.basicConfig(
    filename = os.path.join(LOG_DIR, 'watchdog.log'),
    format='%(asctime)s %(levelname)-5s %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    level=logging.DEBUG
    )
logger = logging.getLogger(__name__)


def main():
    # step 0 init
    last_state = {}
    current_state = {}

    # step 1 read last state
    config = configparser.ConfigParser()
    config.readfp(open(os.path.join(dir_path,'watchdog.cfg')))
    last_state = config._sections['Status']

    # step 2 get current state
    for i in last_state.keys():
        current_state[i] = isActive(i)
        last_state[i] = (last_state[i] == 'True') # convert string "true" to boolean
    
    # extra step: log who is in and who is out
    for i in current_state.keys():
        if current_state[i] != last_state[i]:
            if current_state[i] == True:
                logger.info(ADDRESS_BOOK[i] + ' has arrived')
            else:
                logger.info(ADDRESS_BOOK[i] + ' has left')

    # step 3 analyse state. If changed - enable or disable home mode
    one_was_home = any(last_state.values())
    one_is_home = any(current_state.values())

    if one_was_home != one_is_home:
        if one_is_home:
            setHomeMode()
        else:
            disableHomeMode()

    # step 4 save current state. Do it only if smthng changed
    if last_state != current_state:
        with open(os.path.join(dir_path,'watchdog.cfg'), 'w') as configfile:
            config._sections['Status'] = current_state
            config.write(configfile)


def setHomeMode():
    url = ('https://%s/webapi/entry.cgi?'
        'api=SYNO.SurveillanceStation.ExternalEvent'
        '&method="Trigger"&version=1&eventId=1&eventName="Entering Home Mode"'
        '&account="%s"&password="%s"' % (ADDRESS, LOGIN, PASSWORD))
    r = requests.get(url, verify=False)
    logger.info("Home Mode was set")

def disableHomeMode():
    url = ('https://%s/webapi/entry.cgi?'
        'api=SYNO.SurveillanceStation.ExternalEvent'
        '&method="Trigger"&version=1&eventId=2&eventName="Exiting Home Mode"'
        '&account="%s"&password="%s"' % (ADDRESS, LOGIN, PASSWORD))
    r = requests.get(url, verify=False)
    logger.info("Home Mode was disabled")

def isActive(ip):
    for i in range(0,9):
        ping, _ = scapy.layers.l2.arping(ip, verbose = False)
        if str(ping) == "<ARPing: Other:1>": # <ARPing: Other:0> == not found
            return True
    return False

if __name__ == "__main__":
    main()         
