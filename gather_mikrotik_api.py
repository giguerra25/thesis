from utils import rosApi
from utils import truncate, create_pathdir, timestamp, send2db
#import datetime
#from tinydb import TinyDB



class Gather():

    """
    This is the base class we have to inherit from when writing data gathering
    features for MikroTik devices based on API SSL

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd


    '''def timestamp(self):

        """
        It creates a timestamp
        """

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date'''

    
    def request(self,api_command):

        """
        Function makes an API SSL request, sends an API word to gather data
        from a device

        :param api_command: (str) API word
        """

        response = rosApi(self.ip,self.user,self.passwd,api_command)
        
        date = timestamp()

        return response,date
    

    '''def send2db(self,ip,record,dir):

        """
        Function sends data to the JSON file (database) related to a device and returns 
        the record ID

        :param ip: (str) IP address of the device
        :param record: (str) data to be saved into the JSON file
        :param dir: (str) Path where exists the directory that has the JSON file
        """

        path = create_pathdir(dir)

        db = TinyDB('{}{}.json'.format(path,ip))

        id = db.insert(record)

        return id'''


class GatherInventory(Gather):

    """
    This class creates an instance that collects general data about a MikroTik device
    
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.response, self.date = self.request('/system/resource/print')
        self.dir = '/db/inventory_report'
        #print(self.response)


    def hostname(self):

        """
        Function collects the hostname of a device
        """

        resource = '/system/identity/print'

        #response = ([{'name': 'R1changed'}], '2022-04-12_11:47:09')
        response = self.request(resource)[0][0]     
        hostname = response['name']
        return hostname


    def serial_num(self):

        """
        Function collects the serial number of a device
        """

        resource = '/system/license/print'
        response = self.request(resource)[0][0]
        sn = response['system-id']
        return sn
    

    def version_os(self):

        """
        Function collects the Operative System version of a device
        """

        os = self.response[0]['version']
        return os

    
    def model(self):

        """
        Function collects the model of a device
        """

        model = self.response[0]['board-name']
        return model

    def vendor(self):

        """
        Function collects the vendor of a device
        """

        vendor = self.response[0]['platform']
        return vendor
    

    def inventory_dict(self):

        """
        Function collects different data into a dictionary, then it sends it to the
        JSON file.
        """
        
        values = {
            "Device IP": self.ip,
            "Hostname": self.hostname(),
            "Model": self.model(),
            "Serial Number": self.serial_num(),
            "OS version": self.version_os(),
            "Vendor":self.vendor()
        }
        #id_db = self.send2db(self.ip,values,self.dir)
        id_db = send2db(self.ip, values, self.dir)

        return values, id_db



class GatherCapacity(Gather):

    """
    This class creates an instance that collects general data about physical and
    environmental characteristics of a MikroTik device
    
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.response, self.date = self.request('/system/resource/print')
        self.dir = '/db/capacity_report'

    
    def memory_used(self):

        """
        Function collects used RAM memory in MB and percentage
        """

        response = self.response[0]
        
        #Value transformed from Bytes to MBytes
        free_memory = int(response['free-memory'])
        total_memory = int(response['total-memory'])
        used_memory = total_memory - free_memory
        used_MB = truncate(used_memory/(10**6),2)
        used_percentage = truncate((used_memory/total_memory)*100,1)

        return used_MB, used_percentage


    def cpu_used(self):

        """
        Function collects CPU usage percentage
        """

        response = self.response[0]

        #Value in percentage
        used_cpu = str(response['cpu-load'])

        return used_cpu


    def hdd_used(self):

        """
        Function collects used hard disk in MB and percentage
        """

        response = self.response[0]

        #Value transformed from Bytes to MBytes 
        free_hdd = int(response['free-hdd-space'])
        total_hdd = int(response['total-hdd-space'])
        used_hdd = total_hdd - free_hdd
        used_MB = truncate(used_hdd/(10**6),2)
        used_percentage = truncate((used_hdd/total_hdd)*100,1)
        
        return used_MB, used_percentage


    def interfaces_upordown(self):

        """
        Function collects the number of up and down interfaces
        """

        resource = '/interface/ethernet/print'

        response = self.request(resource)[0]
        
        number_total = len(response)

        number_up = 0

        for interface in response:
            if ("disabled" in interface) and (interface["disabled"]=="false"):
                number_up = number_up+1
        
        number_down = number_total - number_up

        return number_up,number_down


    def capacity_dict(self):

        """
        Function collects different data into a dictionary, then it sends it to the
        JSON file.
        """

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
        #id_db = self.send2db(self.ip, values, self.dir)
        id_db = send2db(self.ip, values, self.dir)

        return values, id_db


#device_list = ['10.0.0.6']
#user = 'giguerra'
#passwd = 'cisco'

#a = GatherCapacity(device_list[0],user,passwd)
#print(a.capacity_dict())

#a = GatherInventory(device_list[0],user,passwd)
#print(a.inventory_dict())