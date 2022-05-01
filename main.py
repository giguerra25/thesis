from simple_term_menu import TerminalMenu
from utils import readfile_devices, ports_mgmt, show_backups
from backup_cisco_napalm import backupNapalm, restoreNapalm
from backup_cisco_netconf import backupNetconf, restoreNetconf
from backup_mikrotik_rest import backupRestApi, restoreRestApi
from backup_mikrotik_api import backupSSLApi, restoreSSLApi
from gather_mikrotik_rest import GatherInventory as gatherMikrotikInventoryRest
from gather_mikrotik_rest import GatherCapacity as gatherMikrotikCapacityRest
from gather_mikrotik_api import GatherInventory as gatherMikrotikInventoryApi
from gather_mikrotik_api import GatherCapacity as gatherMikrotikCapacityApi
from gather_cisco_netconf import GatherInventory as gatherCiscoInventoryNetconf
from gather_cisco_netconf import GatherCapacity as gatherCiscoCapacityNetconf
from gather_cisco_napalm import GatherInventory as gatherCiscoInventoryNapalm
from gather_cisco_napalm import GatherCapacity as gatherCiscoCapacityNapalm
from report_maker import Report
import config_cisco_napalm
import config_mikrotik_api
import config_cisco_netconf
import config_mikrotik_rest
import os

#requests.exceptions.SSLError: HTTPSConnectionPool(host='10.0.0.6', port=443): Max retries exceeded with url: /rest/system/resource (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1131)')))
from requests.exceptions import SSLError
#ncclient.transport.errors.SSHError: Could not open socket to 172.16.1.2:830
from ncclient.transport.errors import SSHError




def backup_cisco(ip,username,passwd,ports):

    print('backup cisco')

    if isinstance(ports['netconf_port'],int):

        backupNetconf(ip,username,passwd)
        return

    if isinstance(ports['ssh_port'],int): 

        backupNapalm(ip,username,passwd)
        return


def backup_mikrotik(ip,username,passwd,ports):

    print('backup mikrotik')

    if isinstance(ports['www-ssl_port'],int):

        backupRestApi(ip,username,passwd)
        return

    if isinstance(ports['api-ssl_port'],int): 

        backupSSLApi(ip,username,passwd)
        return


def restore_backup_cisco(file,ip,username,passwd,ports):

    print('restoring cisco')

    if isinstance(ports['netconf_port'],int):

        print('using NETCONF to restore')
        restoreNetconf(file,ip,username,passwd)
        return

    if isinstance(ports['ssh_port'],int): 

        print('using NAPALM to restore')
        restoreNapalm(file,ip,username,passwd)
        return


def restore_backup_mikrotik(file,ip,username,passwd,ports):

    print('restoring mikrotik')

    if isinstance(ports['www-ssl_port'],int):

        restoreRestApi(file,ip,username,passwd)
        return

    if isinstance(ports['api-ssl_port'],int): 

        restoreSSLApi(file,ip,username,passwd)
        return



def config_cisco(type,ip,username,passwd,config_data,ports):

    if type == 'static':

        if isinstance(ports['netconf_port'],int):
            config_cisco_netconf.ConfigStaticRoute(ip, username, passwd, config_data)
            return
        if isinstance(ports['ssh_port'],int): 
            config_cisco_napalm.ConfigStaticRoute(ip, username, passwd, config_data)
            return
        
    if type == 'interface':
        
        if isinstance(ports['netconf_port'],int):
            config_cisco_netconf.ConfigInterface(ip, username, passwd, config_data)
            return
        if isinstance(ports['ssh_port'],int):
            config_cisco_napalm.ConfigInterface(ip, username, passwd, config_data)
            return


    if type == 'vlans':

        if isinstance(ports['ssh_port'],int):
            config_cisco_napalm.ConfigVlan(ip, username, passwd, config_data)
            return
        if isinstance(ports['netconf_port'],int):
            config_cisco_netconf.ConfigVlan(ip, username, passwd, config_data)
            return

        

def config_mikrotik(type,ip,username,passwd,config_data,ports):

    if type == 'static':

        if isinstance(ports['www-ssl_port'],int):
            config_mikrotik_rest.ConfigStaticRoute(ip, username, passwd, config_data)
            return
        if isinstance(ports['api-ssl_port'],int):
            config_mikrotik_api.ConfigStaticRoute(ip, username, passwd, config_data)
            return
    
    if type == 'interface':

        if isinstance(ports['www-ssl_port'],int):
            config_mikrotik_rest.ConfigInterface(ip, username, passwd, config_data)
            return
        if isinstance(ports['api-ssl_port'],int):
            config_mikrotik_api.ConfigInterface(ip, username, passwd, config_data)
            return

    if type == 'vlans':

        if isinstance(ports['www-ssl_port'],int):
            config_mikrotik_rest.ConfigVlan(ip, username, passwd, config_data)
            return
        if isinstance(ports['api-ssl_port'],int):
            config_mikrotik_api.ConfigVlan(ip, username, passwd, config_data)
            return
        


def gathering_cisco(type,ip,username,passwd,ports):

    """if type == 'inventory':
        #First attempt with NETCONF, then It attempts with NAPALM
        try: 
            gatherCiscoInventoryNetconf(ip,username,passwd).inventory_dict()
        
        except SSHError:
            gatherCiscoInventoryNapalm(ip,username,passwd).inventory_dict()


    if type == 'capacity':
        #First attempt with NETCONF, then It attempts with NAPALM
        try:
            gatherCiscoCapacityNetconf(ip,username,passwd).capacity_dict()
        
        except SSHError:
            gatherCiscoCapacityNapalm(ip,username,passwd).capacity_dict()"""
    
    print('gathering data cisco')

    if type == 'inventory':

        if isinstance(ports['netconf_port'],int):

            gatherCiscoInventoryNetconf(ip,username,passwd).inventory_dict()
            return

        if isinstance(ports['ssh_port'],int): 

            gatherCiscoInventoryNapalm(ip,username,passwd).inventory_dict()
            return
    
    elif type == 'capacity':

        if isinstance(ports['netconf_port'],int):

            gatherCiscoCapacityNetconf(ip,username,passwd).capacity_dict()
            return

        if isinstance(ports['ssh_port'],int): 

            gatherCiscoCapacityNapalm(ip,username,passwd).capacity_dict()
            return


def gathering_mikrotik(type,ip,username,passwd,ports):

    """if type == 'inventory':
        #First attempt with REST API, then It attempts with API SSL
        try:
            gatherMikrotikInventoryRest(ip,username,passwd).inventory_dict()
        
        except SSLError:

            gatherMikrotikInventoryApi(ip,username,passwd).inventory_dict()

    if type == 'capacity':
        #First attempt with REST API, then It attempts with API SSL
        try:
            gatherMikrotikCapacityRest(ip,username,passwd).capacity_dict()

        except SSLError:

            gatherMikrotikCapacityApi(ip,username,passwd).capacity_dict()"""
    
    print('gathering data mikrotik')

    if type == 'inventory':

        if isinstance(ports['www-ssl_port'],int):

            gatherMikrotikInventoryRest(ip,username,passwd).inventory_dict()
            return

        if isinstance(ports['api-ssl_port'],int): 

            gatherMikrotikInventoryApi(ip,username,passwd).inventory_dict()
            return
    
    elif type == 'capacity':

        if isinstance(ports['www-ssl_port'],int):

            gatherMikrotikCapacityRest(ip,username,passwd).capacity_dict()
            return

        if isinstance(ports['api-ssl_port'],int): 

            gatherMikrotikCapacityApi(ip,username,passwd).capacity_dict()
            return
    

def main():

    TITLE = """\nNET_TOOL\n 
    Scripts for Network Automation on Cisco and MikroTik\n"""
    SUBTITLE1 = "\nTypes of reports\n"
    SUBTITLE2 = "\nTypes of configurations\n"

    ITEM_BACKUP = "Make a backup from a device(s)"
    ITEM_RESTORE = "Restore a device(s) with a backup"
    ITEM_REPORT = "Create a report from a device(s)"
    ITEM_CONFIG = "Make configuration changes on a device(s)"

    REPORT_TYPE_1 = "Inventory"
    REPORT_TYPE_2 = "Capacity"

    TYPE_CONFIG_1 = "Configure IP static routes"
    TYPE_CONFIG_2 = "Configure interfaces"
    TYPE_CONFIG_3 = "Configure VLANs"


    main_menu = ["[a] "+ITEM_BACKUP, 
                 "[b] "+ITEM_RESTORE, 
                 "[c] "+ITEM_REPORT, 
                 "[d] "+ITEM_CONFIG,
                 "[q] quit"]

    sub_menu1 = ["[a] "+REPORT_TYPE_1, 
                 "[b] "+REPORT_TYPE_2,
                 "[d] go back"]
    
    sub_menu2 = ["[a] "+TYPE_CONFIG_1, 
                "[b] "+TYPE_CONFIG_2,
                "[c] "+TYPE_CONFIG_3, 
                "[d] go back"]

    terminal_menu = TerminalMenu(main_menu, title=TITLE)
    terminal_submenu1 = TerminalMenu(sub_menu1, title=SUBTITLE1)
    terminal_submenu2 = TerminalMenu(sub_menu2, title=SUBTITLE2)

    #the letter in the square brackets too can use to index the options
    loop = True
    while loop:
        choice = main_menu[terminal_menu.show()]

        #BACKUP
        if choice == main_menu[0]:
            
            list_devices = readfile_devices()
            
            # Make backup sequentially for every device
            for device in list_devices:

                ip = device['mgmt_ip']
                username = device['username']
                passwd = device['password']
                vendor = device['vendor']
                ports = ports_mgmt(device)

                if vendor in ("Cisco", "CISCO", "cisco"):

                    backup_cisco(ip,username,passwd,ports)

                elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                    backup_mikrotik(ip,username,passwd,ports)

            #loop = False

        #RESTORE
        elif choice == main_menu[1]:
            
            list_devices = readfile_devices()
            
            # Make restore sequentially for every device
            for device in list_devices:

                ip = device['mgmt_ip']
                username = device['username']
                passwd = device['password']
                vendor = device['vendor']
                ports = ports_mgmt(device)

                #Submenu to show backups of the device
                file_list = show_backups(ip)
                file_list.append("go back")
                SUBTITLE3 = "\nOptions for device {}:\n".format(ip)
                terminal_submenu3 = TerminalMenu(file_list,title=SUBTITLE3)

                sub_loop3 = True
                while sub_loop3:
                    choice = file_list[terminal_submenu3.show()]

                    if choice != "go back":
                        
                        pwd = os.getcwd()
                        file =  pwd + '/backup_config/' + ip + '/' + choice

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            restore_backup_cisco(file,ip,username,passwd,ports)
                            sub_loop3 = False

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            restore_backup_mikrotik(file,ip,username,passwd,ports)
                            sub_loop3 = False
                    
                    elif choice == "go back":
                        sub_loop3 = False

        #REPORTING
        elif choice == main_menu[2]:
            
            sub_loop1 = True
            while sub_loop1:
                choice = sub_menu1[terminal_submenu1.show()]

                #Inventory report
                if choice == sub_menu1[0]:
                    print (choice)

                    type = 'inventory'
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device['mgmt_ip']
                        username = device['username']
                        passwd = device['password']
                        vendor = device['vendor']
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            gathering_cisco(type,ip,username,passwd,ports)

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            gathering_mikrotik(type,ip,username,passwd,ports)

                        devices_gathered.append(ip)
                    
                    #Report is generated with a list of devices
                    a = Report(devices_gathered,type)
                    a.render_pdfreport()


                #Capacity report
                elif choice == sub_menu1[1]:
                    print (choice)

                    type = 'capacity'
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device['mgmt_ip']
                        username = device['username']
                        passwd = device['password']
                        vendor = device['vendor']
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            gathering_cisco(type,ip,username,passwd,ports)

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            gathering_mikrotik(type,ip,username,passwd,ports)

                        devices_gathered.append(ip)
                    
                    #Report is generated with a list of devices
                    a = Report(devices_gathered,type)
                    a.render_pdfreport()

                
                elif choice == sub_menu1[2]:
                    sub_loop1 = False
     
        #CONFIGURATION
        elif choice == main_menu[3]:
            
            sub_loop2 = True
            while sub_loop2:
                choice = sub_menu2[terminal_submenu2.show()]

                #Configure Static routes
                if choice == sub_menu2[0]:
                    print (choice)

                    type = 'static'
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device['mgmt_ip']
                        username = device['username']
                        passwd = device['password']
                        vendor = device['vendor']
                        config_data = device['routes']
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            config_cisco(type,ip,username,passwd,config_data,ports)

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            config_mikrotik(type,ip,username,passwd,config_data,ports)

                #Configure interfaces
                elif choice == sub_menu2[1]:
                    print (choice)

                    type = 'interface'
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device['mgmt_ip']
                        username = device['username']
                        passwd = device['password']
                        vendor = device['vendor']
                        config_data = device['interfaces']
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            config_cisco(type,ip,username,passwd,config_data,ports)

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            config_mikrotik(type,ip,username,passwd,config_data,ports)
                
                #Configure VLANs
                elif choice == sub_menu2[2]:
                    print (choice)

                    type = 'vlans'
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device['mgmt_ip']
                        username = device['username']
                        passwd = device['password']
                        vendor = device['vendor']
                        config_data = device['vlans']
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            config_cisco(type,ip,username,passwd,config_data,ports)

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            config_mikrotik(type,ip,username,passwd,config_data,ports)

                elif choice == sub_menu2[3]:
                    sub_loop2 = False

        elif choice == main_menu[4]:
            loop = False

main()
