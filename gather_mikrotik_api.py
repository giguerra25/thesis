from utils import rosApi, createNameBackup, createPathBackup
from utils import truncate, create_pathdir
import datetime
from tinydb import TinyDB



class Gather():


    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.url = 'https://'+ip+'/rest'


    def timestamp(self):

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date

    
    def request(self,api_command):

        response = rosApi(self.ip,self.user,self.passwd,api_command)
        
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
        self.response, self.date = self.request('/system/resource/print')
        self.dir = '/db/inventory_report'
        #print(self.response)


    def hostname(self):

        resource = '/system/identity/print'

        #response = ([{'name': 'R1changed'}], '2022-04-12_11:47:09')
        response = self.request(resource)[0][0]     
        hostname = response['name']
        return hostname


    def serial_num(self):

        resource = '/system/license/print'
        response = self.request(resource)[0][0]
        sn = response['system-id']
        return sn
    

    def version_os(self):

        os = self.response[0]['version']
        return os

    
    def model(self):

        model = self.response[0]['board-name']
        return model

    def vendor(self):

        vendor = self.response[0]['platform']
        return vendor
    

    def inventory_dict(self):
        
        values = {
            "Device IP": self.ip,
            "Model": self.model(),
            "Serial Number": self.serial_num(),
            "OS version": self.version_os(),
            "Model": self.model(),
            "Vendor":self.vendor()
        }

        dir = '/db/inventory_report'

        id_db = self.send2db(self.ip,values,self.dir)

        return values, id_db



class GatherCapacity(Gather):

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.response, self.date = self.request('/system/resource/print')
        self.dir = '/db/capacity_report'

    
    def memory_used(self):

        response = self.response[0]
        
        #Value transformed from Bytes to MBytes
        free_memory = int(response['free-memory'])
        total_memory = int(response['total-memory'])
        used_memory = total_memory - free_memory
        used_MB = truncate(used_memory/(10**6),2)
        used_percentage = truncate((used_memory/total_memory),2)*100

        return used_MB, used_percentage


    def cpu_used(self):

        response = self.response[0]

        #Value in percentage
        used_cpu = str(response['cpu-load'])

        return used_cpu


    def hdd_used(self):

        response = self.response[0]

        #Value transformed from Bytes to MBytes 
        free_hdd = int(response['free-hdd-space'])
        total_hdd = int(response['total-hdd-space'])
        used_hdd = total_hdd - free_hdd
        used_MB = truncate(used_hdd/(10**6),2)
        used_percentage = truncate((used_hdd/total_hdd),2)*100
        
        return used_MB, used_percentage


    def interfaces_upordown(self):

        resource = '/interface/ethernet/print'

        response = self.request(resource)[0]
        
        number_total = len(response)

        number_up = 0

        for interface in response:
            if ("disabled" in interface) and (interface["disabled"]=="false"):
                number_up = number_up+1
        
        number_down = number_total - number_up

        list_interfaces = [
                            number_up,
                            number_down
                        ]
        return list_interfaces


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


