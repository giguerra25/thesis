from backup_cisco_napalm import backup, restore
import os

device_list = ['172.16.1.2','172.16.1.254']
user = 'giguerra'
passwd = 'cisco'

bef = 'nochange_config'
aft = 'change_config'
#backup(device_list[0],user,passwd)

restore(os.getcwd()+'/backup_config/'+aft,device_list[0],user,passwd)