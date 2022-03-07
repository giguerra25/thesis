from backup_cisco_napalm import backupNapalm, restoreNapalm
from backup_cisco_netconf import backupNetconf, restoreNetconf
from backup_mikrotik_rest import backupRestApi, restoreRestApi
import os

device_list = ['172.16.1.2','172.16.1.254','10.0.0.2']
user = 'giguerra'
passwd = 'cisco'
dir = os.getcwd()+'/backup_config/'
bef = 'nochange_config'
aft = 'change_config'

#Napalm
#backupNapalm(device_list[0],user,passwd)
#restoreNapalm(dir+'nochange_config_S1',device_list[0],user,passwd)

#NETCONF
#backupNetconf(device_list[1],user,passwd)
#restoreNetconf(dir+'change_config_R3.xml',device_list[1],user,passwd)

#RESTAPI
#backupRestApi(device_list[2],user,passwd)
#restoreRestApi(dir+'change_config_R2.backup',device_list[2],user,passwd)