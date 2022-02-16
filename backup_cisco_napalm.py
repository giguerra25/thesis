from napalm import get_network_driver
import datetime, os

#device_list = ['172.16.1.2','172.16.1.254']
#user = 'giguerra'
#passwd = 'cisco'

def backup(ip,user,passwd):
    
    path = os.getcwd()

    try:
        os.stat(path+'/backup_config')
    except:
        os.mkdir(path+'/backup_config')

    #device_list = ['172.16.1.2','172.16.1.254']

    #user = 'giguerra'
    #passwd = 'cisco'

    driver = get_network_driver('ios')
    #pp = pprint.PrettyPrinter(indent=4)

    with driver(hostname=ip, username=user, password=passwd) as device:

        config = device.get_config(retrieve='running')
        run_conf = config['running']
        
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    with open(path+'/backup_config/'+ip+'_'+date+'_'+'running-config','w') as file:

        file.write(run_conf)
            #pp.pprint(run_conf)

def restore(file,ip,user,passwd):
    
    path = os.getcwd()+'/backup_config'

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