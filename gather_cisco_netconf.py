from ncclient import manager
from utils import xmltree_tag, xmltree_countupdown, xmltree_core
from utils import truncate, timestamp, send2db
import constants as C




class Gather():

    """
    This is the base class we have to inherit from when writing data gathering
    features for Cisco devices based on NETCONF

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
    


    def request(self,filter):

        """
        Function makes a NETCONF RPC request, sends a XML filter to gather data
        from a device

        :param filter: (str) XML filter
        """

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
        
        date = timestamp()

        return response,date




class GatherInventory(Gather):

    """
    This class creates an instance that collects general data about a Cisco device
    
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.dir = '/db/inventory_report'


    def hostname(self):

        """
        Function collects the hostname of a device
        """
        
        #rpc = 'get(C.filter_hostname)'
        #response = self.request(rpc)

        filter = C.filter_hostname
        response = self.request(filter)[0]
        hostname = xmltree_tag(response,'hostname')
  
        return hostname



    def serial_num(self):

        """
        Function collects the serial number of a device
        """

        filter = C.filter_serialnumber
        response = self.request(filter)[0]
        sn = xmltree_tag(response,'sn')

        return sn


    def version_os(self):

        """
        Function collects the Operative System version of a device
        """

        filter = C.filter_osversion
        response = self.request(filter)[0]
        os = xmltree_tag(response,'os')

        return os


    def model(self):

        """
        Function collects the model of a device
        """

        filter = C.filter_model
        response = self.request(filter)[0]
        model = xmltree_tag(response,'model')

        return model

    def vendor(self):

        """
        Function collects the vendor of a device
        """

        vendor = 'Cisco'

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
    environmental characteristics of a Cisco device
    
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        Gather.__init__(self, ip, user, passwd)
        self.dir = '/db/capacity_report'


    def memory_used(self):

        """
        Function collects used RAM memory in MB and percentage
        """

        filter = C.filter_memoryused
        response = self.request(filter)[0]

        used_num = xmltree_tag(response,'mem_used_KB') #value on KB
        used_MB = truncate(int(used_num)/(10**3),2)

        used_percentage = truncate(float(xmltree_tag(response,'mem_used_%')),1)

        return used_MB, used_percentage
    

    def cpu_used(self):

        """
        Function collects CPU usage percentage
        """

        filter = C.filter_cpuused
        response = self.request(filter)[0]
        used_cpu = xmltree_core(response)
        used_cpu = str(used_cpu)

        return used_cpu
    

    def hdd_used(self):

        """
        Function collects used hard disk in MB and percentage
        """
        
        # Value on bits
        filter = C.filter_hddused
        response = self.request(filter)[0]
        used_b = int(xmltree_tag(response,'hdd_used_b'))
        total_b = int(xmltree_tag(response,'hdd_total_b'))

        used_MB = truncate((used_b/8)/(10**6),2)
        used_percentage = truncate((used_b/total_b)*100,1)
        
        return used_MB, used_percentage


    def interfaces_upordown(self):

        """
        Function collects the number of up and down interfaces
        """
        
        filter = C.filter_interfacesupdown
        response = self.request(filter)[0]

        number_up, number_down  = xmltree_countupdown(response)

        return number_up, number_down


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
            "Timestamp": timestamp()
        }

        #id_db = self.send2db(self.ip, values, self.dir)
        id_db = send2db(self.ip, values, self.dir)

        return values, id_db




#device_list = ['172.16.1.254','sandbox-iosxe-recomm-1.cisco.com']
#user = 'giguerra'
#passwd = 'cisco'

#a = GatherCapacity(device_list[0],user,passwd)
#a = GatherCapacity(device_list[1],'developer','C1sco12345')
#print(a.capacity_dict())

#a = GatherInventory(device_list[0],user,passwd)
#print(a.inventory_dict())