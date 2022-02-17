from napalm import get_network_driver
import datetime, os
from utils import createPathBackup, createNameBackup

#device_list = ['172.16.1.2','172.16.1.254']
#user = 'giguerra'
#passwd = 'cisco'

def backupNapalm(ip,user,passwd):
    
    path = createPathBackup()

    driver = get_network_driver('ios')

    with driver(hostname=ip, username=user, password=passwd) as device:

        config = device.get_config(retrieve='running')
        run_conf = config['running']
        
    filename =  createNameBackup(ip)

    with open(path+filename,'w') as file:

        file.write(run_conf)


def restoreNapalm(file,ip,user,passwd):
    
    path = createPathBackup()

    driver = get_network_driver('ios')

    with driver(hostname=ip, username=user, password=passwd, 
            optional_args={
                #'auto_rollback_on_error': False,  #solves no autorollback on cisco IOS
                'global_delay_factor': 2,  #solves timeout netmiko
                }) as device:

        device.load_replace_candidate(filename=file)
        #print("\nDiff:")
        #print(device.compare_config())
        device.commit_config()
    print("Done.")