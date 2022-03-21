from textwrap import indent
from backup_cisco_napalm import backupNapalm, restoreNapalm
from backup_cisco_netconf import backupNetconf, restoreNetconf
from backup_mikrotik_rest import backupRestApi, restoreRestApi
from gather_mikrotik_rest import Gather, GatherInventory, GatherCapacity
import os
import json


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

'''a = GatherInventory(device_list[2],user,passwd)
print(a.hostname())
print(a.serial_num())
print(a.version_os())
print(a.model())
print(a.vendor())'''

'''a = GatherCapacity(device_list[2],user,passwd)
print(a.memory_used())
print(a.cpu_used())
print(a.hdd_used())
print(a.interfaces_upordown())
print(a.date)'''



#a = GatherCapacity(device_list[2],user,passwd)
#values = a.capacity_dict()
#a = GatherInventory(device_list[2],user,passwd)
#values = a.inventory_dict()
#print(values[1])


from report_maker import Report

ips = ['10.0.0.1','10.0.0.2']

a = Report(ips,'capacity')
#print(a.create_table())
a.render_pdfreport()