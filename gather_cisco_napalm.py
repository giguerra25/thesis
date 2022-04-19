from napalm import get_network_driver
from napalm.base.exceptions import ConnectionException
import datetime, os
from utils import createPathBackup, createNameBackup
from utils import truncate, create_pathdir
from tinydb import TinyDB


class Gather():


    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd


    def timestamp(self):

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date

    
    def request(self,napalm_getter):

        driver = get_network_driver("ios")

        try: #Telnet connection
            device = driver(
                hostname = self.ip,
                username = self.user, 
                password = self.passwd, 
                optional_args = {'port': 23, 'transport':"telnet"}
            )
            device.open()
        
        except ConnectionException:
 
            #SSH connection
            device = driver(
                hostname = self.ip,
                username = self.user, 
                password = self.passwd, 
                optional_args = {'port':22}
            )
            device.open()

        response = eval(napalm_getter)

        device.close()
        
        date = self.timestamp()

        return response,date
    

    def send2db(self,ip,record,dir):

        path = create_pathdir(dir)

        db = TinyDB('{}{}.json'.format(path,ip))

        id = db.insert(record)

        return id



class GatherInventory(Gather):

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.response, self.date = self.request('device.get_facts()')
        self.dir = '/db/inventory_report'

    
    def hostname(self):
  
        hostname = self.response['hostname']
        return hostname
    

    def serial_num(self):

        sn = self.response['serial_number']
        return sn

    
    def version_os(self):

        os = self.response['os_version']
        return os
    

    def model(self):

        model = self.response['model']
        return model


    def vendor(self):

        vendor = self.response['vendor']
        return vendor
    

    def inventory_dict(self):
        
        values = {
            "Device IP": self.ip,
            "Hostname": self.hostname(),
            "Model": self.model(),
            "Serial Number": self.serial_num(),
            "OS version": self.version_os(),
            "Vendor":self.vendor()
        }

        id_db = self.send2db(self.ip,values,self.dir)

        return values, id_db



class GatherCapacity(Gather):

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.response, self.date = self.request('device.get_environment()')
        #print(self.response)
        self.dir = '/db/capacity_report'
    

    def memory_used(self):

        response = self.response['memory']
        
        #Value transformed from Bytes to MBytes
        total_memory = int(response['available_ram'])
        used_memory = int(response['used_ram'])
        #free_memory = total_memory - used_memory
        used_MB = truncate(used_memory/(10**6),2)
        used_percentage = truncate((used_memory/total_memory)*100,1)

        return used_MB, used_percentage


    def cpu_used(self):

        response = self.response['cpu'][0]

        #Value in percentage
        used_cpu = str(response['%usage'])

        return used_cpu
    


    def hdd_used(self):

        # NAPALM getter does not collect this data!!!
        used_MB = 'NAPALMnotImplemented'
        used_percentage = 'NAPALMnotImplemented'
        
        
        return used_MB, used_percentage

    

    def interfaces_upordown(self):

        napalm_getter = 'device.get_interfaces()'

        response = self.request(napalm_getter)[0]
        
        number_total = len(response)

        number_up = 0

        for interface,content in response.items():
        # This method has problems, counts VLAN interfaces too!!!
            if ("is_enabled" in content.keys()) and (content["is_enabled"]==True):
                number_up = number_up+1
        
        number_down = number_total - number_up

        return number_up,number_down
    


    def capacity_dict(self):

        memory_used = self.memory_used()
        cpu_load = self.cpu_used()
        disk_used = self.hdd_used()
        interfaces = self.interfaces_upordown()
        
        values = {
            "Device IP": self.ip,
            "Memory used (MB)": memory_used[0],
            "Memory used (%)": memory_used[1],
            "CPU load (%)": cpu_load,
            "Disk used (MB)": disk_used[0],
            "Disk used (%)": disk_used[1],
            "Interfaces Up": interfaces[0],
            "Interfaces Dw": interfaces[1],
            "Timestamp": self.date
        }
        id_db = self.send2db(self.ip, values, self.dir)

        return values, id_db


#device_list = ['172.16.1.2']
#user = 'giguerra'
#passwd = 'cisco'

#a = GatherCapacity(device_list[0],user,passwd)
#print(a.capacity_dict())

#a = GatherInventory(device_list[0],user,passwd)
#print(a.inventory_dict())
