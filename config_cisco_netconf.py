from ncclient import manager
import datetime
from jinja2 import Template

class Config():

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd


    def timestamp(self):

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

        return date


    def request(self,payload):

        with manager.connect(host=self.ip, 
                             port='830', 
                             username=self.user,
                             password=self.passwd, 
                             device_params={'name':'csr'}, 
                             hostkey_verify=False) as m:

            #print(m.connected)
            #response = eval(rpc)
            response = m.edit_config(payload,target="running")

        #response = xmltodict.parse(netconf_response.xml)["rpc-reply"]["data"]
        
        #date = self.timestamp()

        return response


class ConfigInterface(Config):

    def __init__(self, ip, user, passwd, param_interface={}):
        super().__init__(ip, user, passwd)

        self.interface = {
            "name":  param_interface.get("name",""),
            "description": param_interface.get("description",""),
            "ipaddress": param_interface.get("ipaddress",""),
            "ipmask": param_interface.get("ipmask","")
        }
        

    def config_if(self):

        netconf_template = open("templates/netconf_template/config_ietf_interfaces.xml").read()
        
        netconf_payload = netconf_template.format(int_name=self.interface["name"],
                                          int_desc=self.interface["description"],
                                          ip_address=self.interface["ipaddress"],
                                          subnet_mask=self.interface["ipmask"]
                                        )
        #print(payload)
        response = self.request(netconf_payload)

        return response


class ConfigStaticRoute(Config):

    def __init__(self, ip, user, passwd, list_routes=[]):
        super().__init__(ip, user, passwd)

        self.list_routes = list_routes


    def config_routes(self):

        netconf_template = Template(open("templates/netconf_template/config_ietf_static_route.xml").read())

        netconf_payload = netconf_template.render(route_list=self.list_routes)
        #print(netconf_payload)
        response = self.request(netconf_payload)

        return response




"""
param = {
    "name":"GigabitEthernet1",
    "description": "Configured via NETCONF",
    "ipaddress": "10.10.10.1",
    "ipmask":"255.255.255.0"
}
a = ConfigInterface('172.16.1.254','giguerra','cisco',param)

print(a.config_if())"""

routes = [
    {
        "destination_prefix":"1.1.1.0/24",
        "next_hop_address": "10.0.0.2"
    },
    {
        "destination_prefix":"2.2.2.0/24",
        "next_hop_address": "10.0.0.2"
    }
]

a = ConfigStaticRoute('172.16.1.254','giguerra','cisco',routes)
print(a.config_routes())

respuesta = """
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:fd989d21-29a0-42c2-9335-89918facf2fb" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></rpc-reply>
"""