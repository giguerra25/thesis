from napalm import get_network_driver
from utils import createPathBackup, createNameBackup


def backupNapalm(ip,user,passwd):

    """
    Function makes a NAPALM call, collects the running configuration data from 
    a device and creates a file with it.

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """
    
    path = createPathBackup(ip)

    # NAPALM call to collect configuration from Cisco IOS device
    driver = get_network_driver('ios')
    with driver(hostname=ip, username=user, password=passwd) as device:
        config = device.get_config(retrieve='running')
        run_conf = config['running']

    # Create a file with the configuration gathered    
    filename =  createNameBackup(ip,'napalm')
    with open(path+filename,'w') as file:
        file.write(run_conf)


def restoreNapalm(file,ip,user,passwd):

    """
    Function makes a NAPALM call, sends a file with running configuration data to 
    a device and commits the change.

    :param file: (str) Path to the file with the configuration
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """
    
    path = createPathBackup(ip) #CHECK IF IT IS NECESSARY

    # NAPALM call to send configuration to Cisco IOS device
    driver = get_network_driver('ios')
    with driver(hostname=ip, 
                username=user, 
                password=passwd, 
                optional_args={
                    #'auto_rollback_on_error': False,  #solves no autorollback on cisco IOS
                    'global_delay_factor': 2,  #solves timeout netmiko
                    }) as device:

        device.load_replace_candidate(filename=file)
        #print("\nDiff:")
        #print(device.compare_config())
        device.commit_config()
    print("Done.")