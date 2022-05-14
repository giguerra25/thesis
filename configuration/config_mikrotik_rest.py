import requests
from requests.auth import HTTPBasicAuth
import json


class ConfigRestApi:

    """
    This is the base class we have to inherit from when writing configuration
    features for MikroTik devices based on REST API

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.url = "https://" + ip + "/rest"

    def request_put(self, resource, data):

        """
        Function makes a REST API PUT request to create a resource in the running
        configuration.

        :param resource: (str) HTTP resource
        :param data: (list) Parameters of the API request body
        """

        response = requests.put(
            self.url + resource,
            auth=HTTPBasicAuth(self.user, self.passwd),
            data=json.dumps(data),
            verify=False,
            timeout=2,
        )

        response = response.json()
        # date = self.timestamp()
        return response

    def request_patch(self, resource, data):

        """
        Function makes a REST API PATCH request to modify a resource in the running
        configuration.

        :param resource: (str) HTTP resource
        :param data: (list) Parameters of the API request body
        """

        response = requests.patch(
            self.url + resource,
            auth=HTTPBasicAuth(self.user, self.passwd),
            data=json.dumps(data),
            verify=False,
            timeout=2,
        )

        response = response.json()
        # date = self.timestamp()
        return response

    def request_get(self, resource):

        """
        Function makes a REST API GET request to collect data about a resource
        in the running configuration.

        :param resource: (str) HTTP resource
        """

        response = requests.get(
            self.url + resource,
            auth=HTTPBasicAuth(self.user, self.passwd),
            verify=False,
            timeout=2,
        )

        response = response.json()
        # date = self.timestamp()
        return response


class ConfigInterface(ConfigRestApi):

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
        to suitable keys for REST API body data format.

        :param interfaces: (list) List of interfaces with their parameters
        """

        v = {}
        t = []
        for interface in interfaces:

            v["interface"] = interface["interface"]
            v["comment"] = interface["description"]
            v["address"] = interface["ip_address"]
            v["network"] = interface["subnetmask"]
            v["disabled"] = "no" if interface["enabled"] == True else "yes"

            t.append(v)
            v = {}

        return t

    def config_if(self):

        """
        Function sends a REST API REQUEST with interface configuration data.
        """

        resource = "/ip/address"

        for intf in self.interfaces:

            response = self.request_put(resource, intf)
            #print(response)


class ConfigStaticRoute(ConfigRestApi):

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

    def __init__(self, ip, user, passwd, list_routes: list):
        super().__init__(ip, user, passwd)

        self.list_routes = self.changekeys_route(list_routes)

        self.config_routes()

    def changekeys_route(self, routes):

        """
        Function changes keys from data read in YAML file
        to suitable keys for REST API body data format.

        :param routes: (list) List of routes with their parameters
        """

        v = {}
        t = []
        for route in routes:

            v["dst-address"] = route["destination_network"]
            v["gateway"] = str(route["nexthop"])
            v["distance"] = str(route["distance"])
            t.append(v)
            v = {}

        return t

    def config_routes(self):

        """
        Function sends a REST API REQUEST with static route configuration data.
        """

        resource = "/ip/route"

        for route in self.list_routes:
            response = self.request_put(resource, route)
            #print(response) # search 'error': 400


class ConfigVlan(ConfigRestApi):

    """
    This class creates an instance that configures VLANs on a MikroTik device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param list_vlans: (list) List of VLANs with their parameters

    Example of param_interfaces:
        vlans =[{
                    "name": "vlan-80",
                    "id": 80,
                    "ports": [
                        "ether4",
                        "ether5"
                        ]
                }]
    """

    def __init__(self, ip, user, passwd, list_vlans: list):
        super().__init__(ip, user, passwd)

        self.list_vlan = list_vlans

        self.config_vlans()

    def config_vlans(self):

        """
        Function sends a REST API REQUEST with VLAN configuration data.
        """

        resource_bridge = "/interface/bridge"
        resource_port = "/interface/bridge/port"
        resource_vlan = "/interface/bridge/vlan"

        # verifying if Bridge1 exists, if not, then it will be created
        response = self.request_get(resource_bridge)

        for int_bridge in response:
            if "bridge1" in int_bridge.values():
                id_bridge1 = int_bridge[".id"]
                content = {"vlan-filtering": "true"}
                self.request_patch(resource_bridge + "/" + id_bridge1, content)

        if response == []:
            self.request_put(
                resource_bridge, {"name": "bridge1", "vlan-filtering": "true"}
            )

        # request to create ports with PVID
        for vlan in self.list_vlan:

            for port in vlan["ports"]:

                content = {
                    "bridge": "bridge1",
                    "interface": port,
                    "pvid": str(vlan["id"]),
                }

                self.request_put(resource_port, content)

            # request to create VLANs with ports assigned
            content = {
                "bridge": "bridge1",
                "untagged": ",".join(vlan["ports"]),
                "vlan-ids": str(vlan["id"]),
            }

            self.request_put(resource_vlan, content)


device_list = ["10.0.0.2"]
user = "giguerra"
passwd = "cisco"

interfaces = [
    {
        "interface": "ether4",
        "ip_address": "2.2.2.1",
        "subnetmask": "255.255.255.0",
        "description": "Configured via RESTAPI",
        "enabled": True,
    },
    {
        "interface": "ether5",
        "ip_address": "3.3.3.1",
        "subnetmask": "255.255.255.0",
        "description": "Configured via RESTAPI",
        "enabled": True,
    },
]

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
        "name": "vlan-80",
        "id": 80,
        "ports": ["ether4", "ether5"],
    },
    {
        "name": "vlan-90",
        "id": 90,
        "ports": ["ether6", "ether7"],
    },
]
# a = ConfigVlan(device_list[0],user,passwd,vlans)
# a.config_vlans()
