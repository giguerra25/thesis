from ncclient import manager
from utils import createPathBackup, createNameBackup, stripTagXml
from utils import xmltree_tag, xmltree_countupdown, xmltree_core
from utils import truncate, create_pathdir
import datetime
from tinydb import TinyDB
import constants as C




class Gather():


    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
    

    def timestamp(self):

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date
    

    def send2db(self,ip,record,dir):

        path = create_pathdir(dir)

        db = TinyDB('{}{}.json'.format(path,ip))

        id = db.insert(record)

        return id
    


    def request(self,filter):

        with manager.connect(host=self.ip, 
                             port='830', 
                             username=self.user,
                             password=self.passwd, 
                             device_params={'name':'csr'}, 
                             hostkey_verify=False) as m:

            #print(m.connected)
            #response = eval(rpc)
            response = m.get(filter).data_xml

        #response = xmltodict.parse(netconf_response.xml)["rpc-reply"]["data"]
        
        date = self.timestamp()

        return response,date




class GatherInventory(Gather):

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.dir = '/db/inventory_report'


    def hostname(self):
        
        #rpc = 'get(C.filter_hostname)'
        #response = self.request(rpc)

        filter = C.filter_hostname
        response = self.request(filter)[0]
        hostname = xmltree_tag(response,'hostname')
  
        return hostname



    def serial_num(self):

        filter = C.filter_serialnumber
        response = self.request(filter)[0]
        sn = xmltree_tag(response,'sn')

        return sn


    def version_os(self):

        filter = C.filter_osversion
        response = self.request(filter)[0]
        os = xmltree_tag(response,'os')

        return os


    def model(self):

        filter = C.filter_model
        response = self.request(filter)[0]
        model = xmltree_tag(response,'model')

        return model

    def vendor(self):

        vendor = 'Cisco'

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
        self.dir = '/db/capacity_report'

    def memory_used(self):

        filter = C.filter_memoryused
        response = self.request(filter)[0]

        used_num = xmltree_tag(response,'mem_used_KB') #value on KB
        used_MB = truncate(int(used_num)/(10**3),2)

        used_percentage = truncate(float(xmltree_tag(response,'mem_used_%')),1)

        return used_MB, used_percentage
    
    def cpu_used(self):

        filter = C.filter_cpuused
        response = self.request(filter)[0]
        used_cpu = xmltree_core(response)
        used_cpu = str(used_cpu)

        return used_cpu
    

    def hdd_used(self):
        
        # Value on bits
        filter = C.filter_hddused
        response = self.request(filter)[0]
        used_b = int(xmltree_tag(response,'hdd_used_b'))
        total_b = int(xmltree_tag(response,'hdd_total_b'))

        used_MB = truncate((used_b/8)/(10**6),2)
        used_percentage = truncate((used_b/total_b)*100,1)
        
        return used_MB, used_percentage


    def interfaces_upordown(self):
        
        filter = C.filter_interfacesupdown
        response = self.request(filter)[0]

        number_up, number_down  = xmltree_countupdown(response)

        return number_up, number_down


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
            "Timestamp": self.timestamp()
        }

        id_db = self.send2db(self.ip, values, self.dir)

        return values, id_db




#device_list = ['172.16.1.254','sandbox-iosxe-recomm-1.cisco.com']
#user = 'giguerra'
#passwd = 'cisco'

#a = GatherCapacity(device_list[0],user,passwd)
#a = GatherCapacity(device_list[1],'developer','C1sco12345')
#print(a.capacity_dict())

#a = GatherInventory(device_list[0],user,passwd)
#print(a.inventory_dict())