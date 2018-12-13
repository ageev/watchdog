# watchdog
Synology surveillance station home mode watchdog

# idea
Geofence feature of Synology app doesn't work for me well, so I've decided to build my own. 
If one of the phones defined in cfg file will be detected in Wi-Fi network, web request will be generated to set Home Mode and vice versa
E.g. if you (or any family members) are home - alarm will be switched off automatically 

# prerequisites
Configure Home Mode (e.g. switch off motion detection)
You need to set to Actions first in Surveilance Station software:
Action 1 - enable Home Mode by external command. Double check that URL generated match the one in the script
Action 2 - disable Home Mode by external command
Scapy, requests. configparser python modules

# installation 
add phones to watchdog.cfg
customise login&password&ip&address_book in the script
copy to /usr/local/sbin 
set schedule:
sudo crontab -e
* * * * * /usr/bin/python /usr/local/sbin/watchdog.py > /dev/null 2>&1

check logs after a while
cat /usr/local/sbin/watchdog.log
