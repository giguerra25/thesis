from napalm import get_network_driver
from netmiko import ConnectHandler
from napalm.base.exceptions import ConnectionException
import datetime
from jinja2 import Template
import os

class Config():

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd


    def timestamp(self):

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date

    
    def request(self,napalm_config):

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

    def __init__(self, ip, user, passwd, param_interfaces=[]):
        super().__init__(ip, user, passwd)

        self.interfaces = param_interfaces
    
    def config_if(self):

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

    def __init__(self, ip, user, passwd, list_routes=[]):
        super().__init__(ip, user, passwd)

        self.list_routes = list_routes

    def config_routes(self):

        napalm_template = Template(open("templates/napalm_template/config_static_route.j2").read())

        configuration_data = napalm_template.render(route_list=self.list_routes)
        print(configuration_data)

        self.request(configuration_data)


class ConfigVlan(Config):

    def __init__(self, ip, user, passwd, list_vlans=[]):
        super().__init__(ip, user, passwd)

        self.list_vlan = list_vlans


    def netmikoconfig(self,command):

        device = {"device_type":'cisco_ios',
                  "ip":self.ip,
                  "username":self.user,
                  "global_delay_factor": 2,
                  "password":self.passwd}

        net = ConnectHandler(**device)
        output = net.send_config_set(command)
        return output

    def config_vlans(self):

        napalm_template = Template(open("templates/napalm_template/config_vlan.j2").read())

        configuration_data = napalm_template.render(vlan_list=self.list_vlan)
        #print(configuration_data)

        #VLAN creation using Netmiko
        conf_vlan = []
        for vlan in self.list_vlan:
            conf_vlan.append("vlan {}".format(vlan["id"]))
            conf_vlan.append("name {}".format(vlan["name"]))
        #print(conf_vlan)

        self.netmikoconfig(conf_vlan)
        self.request(configuration_data)


param = [
    {
    "name":"Vlan177",
    "description": "Configured via NAPALM",
    "address": "10.77.1.68 255.255.255.0",
    "enabled": True
    }
]


#a = ConfigInterface('172.16.1.2','giguerra','cisco',param)
#a.config_if()

routes =[
    {
        "network": "1.1.1.0",
        "mask": "255.255.255.0",
        "interface": "Vlan30",
        "distance": "10"
    }
]

#a = ConfigStaticRoute('172.16.1.2','giguerra','cisco',routes)
#a.config_routes()


vlans =[
    {
        "name": "vlan-150",
        "id": "150",
        "interfaces": [
            "GigabitEthernet3/2",
            "GigabitEthernet3/3",
        ],
    },
    {
        "name": "vlan-120",
        "id": "120",
        "interfaces": [
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


a = ConfigVlan('172.16.1.2','giguerra','cisco',vlans)
a.config_vlans()
