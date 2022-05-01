from ncclient import manager
from jinja2 import Template

class Config():

    """
    This is the base class we have to inherit from when writing configuration
    features for Cisco devices based on NETCONF

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd



    def request(self,payload):

        """
        Function makes a NETCONF RPC call, sends configuration data to merge it with the
        running configuration on a device

        :param payload: (str) It is the configuration data, which must be rooted in the 
                              `config` element. It can be specified either as a 
                              string or an :class:`~xml.etree.ElementTree.Element`.
        """


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

    """
    This class creates an instance that configures interfaces of a Cisco device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param param_interfaces: (list) List of interfaces with their parameters

    Example of param_interfaces:
        interfaces = [{
                        "interface": "GigabitEthernet1",
                        "description": "Configured via NETCONF",
                        "ip_address": "10.10.10.1",
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
        Function reads an XML template, fills it with interface data, and sends a
        NETCONF RPC call with this data.
        """

        netconf_template = Template(open("templates/netconf_template/config_ietf_interfaces.xml").read())
        
        netconf_payload = netconf_template.render(interfaces=self.interfaces)
        #print(payload)
        response = self.request(netconf_payload)

        #return response

class ConfigStaticRoute(Config):

    """
    This class creates an instance that configures static routes on a Cisco device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param list_routes: (list) List of interfaces with their parameters

    Example of list_routes:
        routes =[{
                    "destination_network": "1.1.1.0/24",
                    "nexthop": "172.16.1.254",
                    "distance": 10
                }]
    """

    def __init__(self, ip, user, passwd, list_routes=[]):
        super().__init__(ip, user, passwd)

        self.list_routes = list_routes

        self.config_routes()


    def config_routes(self):

        """
        Function reads an XML template, fills it with routes data, and sends a
        NETCONF RPC call with this data.
        """

        netconf_template = Template(open("templates/netconf_template/config_ietf_static_route.xml").read())

        netconf_payload = netconf_template.render(route_list=self.list_routes)
        #print(netconf_payload)
        response = self.request(netconf_payload)

        #return response




param = {
    "interface":"GigabitEthernet1",
    "description": "Configured via NETCONF",
    "ip_address": "10.10.10.1",
    "subnetmask":"255.255.255.0",
    "enabled": True
}
#a = ConfigInterface('172.16.1.254','giguerra','cisco',param)
#print(a.config_if())

routes = [
    {
        "destination_network":"1.1.1.0/24",
        "nexthop": "10.0.0.2",
        "distance": 10
    },
    {
        "destination_network":"2.2.2.0/24",
        "nexthop": "10.0.0.2",
        "distance": 10
    }
]

#a = ConfigStaticRoute('172.16.1.254','giguerra','cisco',routes)
#print(a.config_routes())

#respuesta = """<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:fd989d21-29a0-42c2-9335-89918facf2fb" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><ok/></rpc-reply>"""