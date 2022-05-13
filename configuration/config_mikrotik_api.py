from utils import rosApi
from jinja2 import Template


class ConfigApi:

    """
    This is the base class we have to inherit from when writing configuration
    features for MikroTik devices based on API SSL

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd

    def request(self, api_commands):

        """
        Function makes an API SSL call, sends commands to a device to make changes
        on running configuration.

        :param api_commands: (str, tuple, list) API words that go in the API request
        """

        response = rosApi(self.ip, self.user, self.passwd, api_commands)

        # date = self.timestamp()

        return response


class ConfigInterface(ConfigApi):

    """
    This class creates an instance that configures interfaces of a MikroTik device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param param_interfaces: (list) List of interfaces with their parameters

    Example of param_interfaces:
        interfaces = [{
                        "interface":"ether3",
                        "ip_address": "2.2.2.1",
                        "subnetmask": "255.255.255.0",
                        "description": "Configured via APISSL",
                        "enabled": True
                        }]
    """

    def __init__(self, ip, user, passwd, param_interfaces: list):
        super().__init__(ip, user, passwd)

        self.interfaces = self.changekeys_interface(param_interfaces)

        self.config_if()

    def changekeys_interface(self, interfaces):

        """
        Function changes keys from data read in YAML file
        to suitable keys for the API word command and its attributes.

        :param interfaces: (list) List of interfaces with their parameters
        """

        v = {}
        t = []
        for interface in interfaces:

            v["interface"] = interface["interface"]
            # hack to solve problem about sending description with API SSL
            v["comment"] = interface["description"].replace(" ", "_")
            v["address"] = interface["ip_address"]
            v["network"] = interface["subnetmask"]
            v["disabled"] = "no" if interface["enabled"] == True else "yes"

            t.append(v)
            v = {}

        return t

    def config_if(self):

        """
        Function reads a JINJA template, fills it with interface data, and sends a
        API SSL call with this data.
        """

        apissl_template = Template(
            open("templates/apissl_template/config_int.j2").read()
        )

        apissl_payload = []

        for intf in self.interfaces:
            apissl_payload.append(apissl_template.render(interface=intf))

        # print(apissl_payload)

        self.request(apissl_payload)


class ConfigStaticRoute(ConfigApi):

    """
    This class creates an instance that configures static routes on a MikroTik device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param list_routes: (list) List of interfaces with their parameters

    Example of list_routes:
        routes =[{
                    "destination_network": "172.168.30.0/24",
                    "nexthop": "5.5.5.5",
                    "distance": 1
                }]
    """

    def __init__(self, ip, user, passwd, list_routes=[]):
        super().__init__(ip, user, passwd)

        self.list_routes = self.changekeys_route(list_routes)

        self.config_routes()

    def changekeys_route(self, routes):

        """
        Function makes string values of nexthop and distance for API SSL
        body data format

        :param routes: (list) List of routes with their parameters
        """

        v = {}
        t = []
        for route in routes:

            v["destination_network"] = route["destination_network"]
            v["nexthop"] = str(route["nexthop"])
            v["distance"] = str(route["distance"])
            t.append(v)
            v = {}

        return t

    def config_routes(self):

        """
        Function reads a JINJA template, fills it with routes data, and sends an
        API SSL call with this data.
        """

        apissl_template = Template(
            open("templates/apissl_template/config_static_route.j2").read()
        )

        apissl_payload = []

        for route in self.list_routes:
            apissl_payload.append(apissl_template.render(route=route))

        # print(apissl_payload)

        self.request(apissl_payload)


class ConfigVlan(ConfigApi):

    """
    This class creates an instance that configures VLANs on a MikroTik device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param list_vlans: (list) List of VLANs with their parameters

    Example of param_interfaces:
        vlans =[{
                    "name": "vlan-60",
                    "id": 60,
                    "ports": [
                        "ether3",
                        "ether4",
                         ]
                }]
    """

    def __init__(self, ip, user, passwd, list_vlans=[]):
        super().__init__(ip, user, passwd)

        self.list_vlan = list_vlans

        self.config_vlans()

    def config_vlans(self):

        """
        Function reads a JINJA template, fills it with VLAN data, and sends an
        API SSL call with this data.
        """

        apissl_payload = []

        # verifying if Bridge1 exists, if not, then it will be created
        response = self.request("/interface/bridge/print")

        for int_bridge in response:
            if "bridge1" in int_bridge.values():
                id_bridge1 = int_bridge[".id"]
                apissl_payload.append(
                    "/interface/bridge/set\n=numbers={}\n=vlan-filtering=yes".format(
                        id_bridge1
                    )
                )

        if response == []:
            apissl_payload.append(
                "/interface/bridge/add\n=name=bridge1\n=vlan-filtering=yes"
            )

        # commands to create ports with PVID
        for vlan in self.list_vlan:

            for port in vlan["ports"]:

                apissl_template = Template(
                    open(
                        "templates/apissl_template/config_bridge_port.j2"
                    ).read()
                )
                content = apissl_template.render(
                    vlan={"id": str(vlan["id"]), "port": port}
                )
                apissl_payload.append(content)

            # commands to create VLANs with ports assigned
            apissl_template = Template(
                open("templates/apissl_template/config_bridge_vlan.j2").read()
            )
            content = apissl_template.render(vlan=vlan)
            apissl_payload.append(content)

        """for line in apissl_payload:
            with open('conf2.txt', "a") as f:
                f.write(line)"""

        self.request(apissl_payload)


device_list = ["10.0.0.6"]
user = "giguerra"
passwd = "cisco"
# command = ['/ip/address/add\n=address=2.2.2.1/32\n=interface=ether3\n=disabled=yes\n=comment="fhf hfh fgf gfg"','/ip/address/add\n=address=3.3.3.1/32\n=interface=ether4\n=disabled=yes']
# command = '/ip/address/print'
interfaces = [
    {
        "interface": "ether3",
        "ip_address": "2.2.2.1",
        "subnetmask": "255.255.255.0",
        "description": "Configured via APISSL",
        "enabled": True,
    },
    {
        "interface": "ether4",
        "ip_address": "3.3.3.1",
        "subnetmask": "255.255.255.0",
        "description": "Configured via APISSL",
        "enabled": True,
    },
]

# a = ConfigApi(device_list[0],user,passwd)
# a.request(command)
# a = ConfigInterface(device_list[0],user,passwd,interfaces)
# a.config_if()

routes = [
    {
        "destination_network": "172.168.30.0/24",
        "nexthop": "5.5.5.5",
        "distance": 1,
    },
    {
        "destination_network": "192.168.50.0/24",
        "nexthop": "10.0.3.1",
        "distance": 5,
    },
]
# a = ConfigStaticRoute(device_list[0],user,passwd,routes)
# a.config_routes()

vlans = [
    {
        "name": "vlan-60",
        "id": 60,
        "ports": ["ether3", "ether4"],
    },
    {
        "name": "vlan-70",
        "id": 70,
        "ports": ["ether5", "ether6"],
    },
]

# a = ConfigVlan(device_list[0],user,passwd,vlans)
# a.config_vlans()
