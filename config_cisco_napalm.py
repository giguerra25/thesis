from napalm import get_network_driver
from napalm.base.exceptions import ConnectionException
from jinja2 import Template
from utils import netmikoconfig

class Config():

    """
    This is the base class we have to inherit from when writing configuration
    features for Cisco devices based on NAPALM

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd


    
    def request(self,napalm_config:str):

        """
        Function makes a NAPALM call, sends configuration data to merge it with the
        running configuration on a device

        :param napalm_config: (str) String with configuration data
        """

        driver = get_network_driver("ios")

        try: #Telnet connection
            device = driver(
                hostname = self.ip,
                username = self.user, 
                password = self.passwd, 
                optional_args = {'port': 23, 
                                'transport':"telnet",
                                'global_delay_factor': 2,  #solves timeout netmiko
                                }
            )
            device.open()
        
        except ConnectionException:
 
            #SSH connection
            device = driver(
                hostname = self.ip,
                username = self.user, 
                password = self.passwd, 
                optional_args = {'port':22,
                                'global_delay_factor': 2}
            )
            device.open()

        #device.load_merge_candidate(filename=napalm_config)
        device.load_merge_candidate(config=napalm_config)
        print(device.compare_config())
        device.commit_config()
        device.close()
        
        #date = self.timestamp()
        #return response,date

class ConfigInterface(Config):

    """
    This class creates an instance that configures interfaces of a Cisco device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param param_interfaces: (list) List of interfaces with their parameters

    Example of param_interfaces:
        interfaces = [{
                        "interface": "Vlan177",
                        "description": "Configured via NAPALM",
                        "ip_address": "10.77.1.68",
                        "subnetmask": "255.255.255.0",
                        "enabled": True
                        }]
    """

    def __init__(self, ip, user, passwd, param_interfaces:list):
        super().__init__(ip, user, passwd)

        self.interfaces = param_interfaces
        
        self.config_if()
    

    def config_if(self):

        """
        Function reads a JINJA template, fills it with interface data, and sends a
        NAPALM call with this data.
        """

        napalm_template = Template(open("templates/napalm_template/config_int.j2").read())

        configuration_data = napalm_template.render(interfaces=self.interfaces)

        """output_file = "tmp/conf.txt"
        with open(output_file, "w") as f:
            f.write(configuration_data)
        
        self.request("tmp/conf.txt")

        os.remove("tmp/conf.txt")"""
        print(configuration_data)
        self.request(configuration_data)



class ConfigStaticRoute(Config):

    """
    This class creates an instance that configures static routes on a Cisco device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param list_routes: (list) List of interfaces with their parameters

    Example of param_interfaces:
        routes =[{
                    "destination_network": "1.1.1.0/24",
                    "nexthop": "172.16.1.254",
                    "distance": 10
                }]
    """

    def __init__(self, ip, user, passwd, list_routes:list):
        super().__init__(ip, user, passwd)

        self.list_routes = self.changekeys_route(list_routes)

        self.config_routes()
    

    def changekeys_route(self,routes:list):

        """
        Function changes keys (IPV4 address representation) from data read in 
        YAML file to suitable keys for Cisco CLI configuration file. 

        :param routes: (list) List oof static IP routes

        Example of return:
            routes =[{
                        "network": "1.1.1.0",
                        "mask": "255.255.255.0",
                        "nexthop": "172.16.1.254",
                        "distance": 10
                    }]
        """

        from ipaddress import IPv4Network

        v = {}
        t = []

        for route in routes:
            network = IPv4Network(route['destination_network'])
            ipadd = str(network.network_address)
            mask = str(network.netmask)

            v['network'] = ipadd
            v['mask'] = mask
            v['nexthop'] = str(route['nexthop'])
            v['distance'] = str(route['distance'])
            t.append(v)
            v = {}
        
        return t



    def config_routes(self):

        """
        Function reads a JINJA template, fills it with routes data, and sends a
        NAPALM call with this data.
        """

        napalm_template = Template(open("templates/napalm_template/config_static_route.j2").read())

        configuration_data = napalm_template.render(route_list=self.list_routes)
        #print(configuration_data)

        self.request(configuration_data)



class ConfigVlan(Config):

    """
    This class creates an instance that configures VLANs on a switch Cisco

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param list_vlans: (list) List of VLANs with their parameters

    Example of param_interfaces:
        vlans =[{
                    "name": "vlan-150",
                    "id": 150,
                    "ports": [
                        "GigabitEthernet3/2",
                        "GigabitEthernet3/3",
                        ]
                }]
    """

    def __init__(self, ip, user, passwd, list_vlans:list):
        super().__init__(ip, user, passwd)

        self.list_vlan = list_vlans

        self.config_vlans()



    def config_vlans(self):

        """
        Function reads a JINJA template, fills it with VLAN data, and sends a
        NETMIKO call and NAPALM call with this data.
        """

        napalm_template = Template(open("templates/napalm_template/config_vlan.j2").read())

        configuration_data = napalm_template.render(vlan_list=self.list_vlan)
        #print(configuration_data)

        #VLAN name and ID creation using Netmiko call
        conf_vlan = []
        for vlan in self.list_vlan:
            conf_vlan.append("vlan {}".format(vlan["id"]))
            conf_vlan.append("name {}".format(vlan["name"]))
        #print(conf_vlan)
        netmikoconfig(self.ip,self.user,self.passwd,conf_vlan)
        #self.netmikoconfig(conf_vlan)

        #VLAN port configuration using NAPALM call
        self.request(configuration_data)


interfaces = [
    {
    "interface":"Vlan177",
    "description": "Configured via NAPALM",
    "ip_address": "10.77.1.68",
    "subnetmask": "255.255.255.0",
    "enabled": True
    }
]


#a = ConfigInterface('172.16.1.2','giguerra','cisco',interfaces)
#a.config_if()

routes =[
    {
        "network": "1.1.1.0",
        "mask": "255.255.255.0",
        "nexthop": "172.16.1.254",
        "distance": 10
    }
]

routes2 =[
    {
        "destination_network": "1.1.1.0/24",
        "nexthop": "172.16.1.254",
        "distance": 10
    }
]

#a = ConfigStaticRoute('172.16.1.2','giguerra','cisco',routes2)
#a.config_routes()



vlans =[
    {
        "name": "vlan-150",
        "id": 150,
        "ports": [
            "GigabitEthernet3/2",
            "GigabitEthernet3/3",
        ],
    },
    {
        "name": "vlan-120",
        "id": 120,
        "ports": [
            "GigabitEthernet3/0",
            "GigabitEthernet3/1",
        ],
    }
]

commands = ['vlan 120',
            'name vlan-120',
            'interface GigabitEthernet3/0',
            'switchport',
            'switchport mode access',
            'switchport access vlan 120',
    ]

#a = ConfigVlan('172.16.1.2','giguerra','cisco',vlans)
#a.config_vlans()
