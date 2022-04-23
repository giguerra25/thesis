import datetime
from utils import rosApi
from jinja2 import Template


class Config():

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
    
    def timestamp(self):

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date
    

    def request(self,api_command):

        response = rosApi(self.ip,self.user,self.passwd,api_command)
        
        #date = self.timestamp()

        return response



class ConfigInterface(Config):

    def __init__(self, ip, user, passwd, param_interfaces=[]):
        super().__init__(ip, user, passwd)

        self.interfaces = param_interfaces
    

    def config_if(self):

        apissl_template = Template(open("templates/apissl_template/config_int.j2").read())

        apissl_payload = []

        for intf in self.interfaces:
            apissl_payload.append(apissl_template.render(interface=intf))

        print(apissl_payload)

        self.request(apissl_payload)


class ConfigStaticRoute(Config):

    def __init__(self, ip, user, passwd, list_routes=[]):
        super().__init__(ip, user, passwd)

        self.list_routes = list_routes

    def config_routes(self):

        apissl_template = Template(open("templates/apissl_template/config_static_route.j2").read())

        apissl_payload = []

        for route in self.list_routes:
            apissl_payload.append(apissl_template.render(route=route))
        
        #print(apissl_payload)

        self.request(apissl_payload)

        

    
class ConfigVlan(Config):

    def __init__(self, ip, user, passwd, list_vlans=[]):
        super().__init__(ip, user, passwd)

        self.list_vlan = list_vlans


    def config_vlans(self):

        apissl_payload = []

        #verifying if Bridge1 exists, if not, then it will be created
        response = self.request("/interface/bridge/print")
        
        for int_bridge in response:
            if 'bridge1' in int_bridge.values():
                id_bridge1 = int_bridge['.id']
                apissl_payload.append("/interface/bridge/set\n=numbers={}\n=vlan-filtering=yes".format(id_bridge1))
        
        if response == []:
            apissl_payload.append('/interface/bridge/add\n=name=bridge1\n=vlan-filtering=yes') 
        
        #commands to create ports with PVID
        for vlan in self.list_vlan:

            for port in vlan['ports']:

                apissl_template = Template(open("templates/apissl_template/config_bridge_port.j2").read())
                content = apissl_template.render(vlan={'id':vlan['id'],
                                                       'port':port})
                apissl_payload.append(content)

        #commands to create VLANs with ports assigned
            apissl_template = Template(open("templates/apissl_template/config_bridge_vlan.j2").read())
            content = apissl_template.render(vlan=vlan)
            apissl_payload.append(content)
             
            
        """for line in apissl_payload:
            with open('conf2.txt', "a") as f:
                f.write(line)"""
        

        #a = ('/interface/bridge/port/add','=bridge=bridge1','=interface=ether4', '=pvid=150')
        #a = ['/interface/bridge/port/add\n=bridge=bridge1\n=interface=eth3\n=pvid=150']
        self.request(apissl_payload)





device_list = ['10.0.0.6']
user = 'giguerra'
passwd = 'cisco'
#command = ['/ip/address/add\n=address=2.2.2.1/32\n=interface=ether3\n=disabled=yes\n=comment="fhf hfh fgf gfg"','/ip/address/add\n=address=3.3.3.1/32\n=interface=ether4\n=disabled=yes']
#command = '/ip/address/print'
interfaces = [
    {
    "interface":"ether3",
    "comment": "Configured via APISSL",
    "address": "2.2.2.1/32",
    },
    {
    "interface":"ether4",
    "comment": "Configured via APISSL",
    "address": "3.3.3.1/32",
    }
]

#a = Config(device_list[0],user,passwd)
#a.request(command)
#a = ConfigInterface(device_list[0],user,passwd,interfaces)
#a.config_if()

routes = [
    {
        "destination": "172.168.30.0/24",
        "next_hop": "5.5.5.5",
        "distance": "1"
    },
    {
        "destination": "192.168.50.0/24",
        "next_hop": "10.0.3.1",
        "distance": "5"
    }
]
#a = ConfigStaticRoute(device_list[0],user,passwd,routes)
#a.config_routes()

vlans =[
    {
        "name": "vlan-60",
        "id": "60",
        "ports": [
            "ether3",
            "ether4"
        ],
    },
    {
        "name": "vlan-70",
        "id": "70",
        "ports": [
            "ether5",
            "ether6"
        ],
    }
]

a = ConfigVlan(device_list[0],user,passwd,vlans)
a.config_vlans()