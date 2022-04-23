import requests
from requests.auth import HTTPBasicAuth
import datetime
import json

class Config():

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.url = 'https://'+ip+'/rest'
    
    def timestamp(self):

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date

    def request_put(self,resource,data):

        response = requests.put(self.url+resource,
                                auth=HTTPBasicAuth(self.user,self.passwd),
                                data=json.dumps(data), 
                                verify=False, 
                                timeout=2)
    
        response = response.json()

        #date = self.timestamp()

        return response
    
    def request_patch(self,resource,data):

        response = requests.patch(self.url+resource,
                                auth=HTTPBasicAuth(self.user,self.passwd),
                                data=json.dumps(data), 
                                verify=False, 
                                timeout=2)
    
        response = response.json()

        #date = self.timestamp()

        return response
    
    def request_get(self,resource):

        response = requests.get(self.url+resource,
                                auth=HTTPBasicAuth(self.user,self.passwd),
                                verify=False, 
                                timeout=2)
    
        response = response.json()

        #date = self.timestamp()

        return response


class ConfigInterface(Config):

    def __init__(self, ip, user, passwd, param_interfaces=[]):
        super().__init__(ip, user, passwd)

        self.interfaces = param_interfaces

    def config_if(self):
        
        resource = '/ip/address' 

        for intf in self.interfaces:

            response = self.request_put(resource,intf)
            print(response)



class ConfigStaticRoute(Config):

    def __init__(self, ip, user, passwd, list_routes=[]):
        super().__init__(ip, user, passwd)

        self.list_routes = list_routes

    
    def config_routes(self):

        resource = '/ip/route'

        for route in self.list_routes:
            response = self.request_put(resource,route)
            print(response)


class ConfigVlan(Config):

    def __init__(self, ip, user, passwd, list_vlans=[]):
        super().__init__(ip, user, passwd)

        self.list_vlan = list_vlans
    

    def config_vlans(self):

        resource_bridge = '/interface/bridge'
        resource_port = '/interface/bridge/port'
        resource_vlan = '/interface/bridge/vlan'

        #verifying if Bridge1 exists, if not, then it will be created
        response = self.request_get(resource_bridge)

        for int_bridge in response:
            if 'bridge1' in int_bridge.values():
                id_bridge1 = int_bridge['.id']
                content = {
                    'vlan-filtering':'true'
                }
                self.request_patch(resource_bridge+'/'+id_bridge1,content)
        
        if response == []: 
            self.request_put(resource_bridge,{'name':'bridge1',
                                          'vlan-filtering':'true'})
       #request to create ports with PVID
        for vlan in self.list_vlan:

            for port in vlan['ports']:

                content = { 
                    'bridge':'bridge1',
                    'interface':port,
                    'pvid':vlan['id']
                 }
                
                self.request_put(resource_port,content)

        #request to create VLANs with ports assigned
            content = {
                'bridge':'bridge1',
                'untagged':','.join(vlan['ports']),
                'vlan-ids':vlan['id']
            }

            self.request_put(resource_vlan,content)



device_list = ['10.0.0.2']
user = 'giguerra'
passwd = 'cisco'

interfaces = [
    {
    "interface":"ether4",
    "comment": "Configured via APIREST",
    "address": "2.2.2.1/32",
    },
    {
    "interface":"ether5",
    "comment": "Configured via APIREST",
    "address": "3.3.3.1/32",
    }
]

#a = ConfigInterface(device_list[0],user,passwd,interfaces)
#a.config_if()

routes = [
    {
        "dst-address": "172.168.30.0/24",
        "gateway": "5.5.5.5",
        "distance": "1"
    },
    {
        "dst-address": "192.168.50.0/24",
        "gateway": "10.0.3.1",
        "distance": "5"
    }
]

#a = ConfigStaticRoute(device_list[0],user,passwd,routes)
#a.config_routes()

vlans =[
    {
        "name": "vlan-80",
        "id": "80",
        "ports": [
            "ether4",
            "ether5"
        ],
    },
    {
        "name": "vlan-90",
        "id": "90",
        "ports": [
            "ether6",
            "ether7"
        ],
    }
]
a = ConfigVlan(device_list[0],user,passwd,vlans)
a.config_vlans()