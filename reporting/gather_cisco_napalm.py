from napalm import get_network_driver
from napalm.base.exceptions import ConnectionException
from utils import truncate, timestamp, send2db


class GatherNapalm:

    """
    This is the base class we have to inherit from when writing data gathering
    features for Cisco devices based on NAPALM

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd

    def request(self, napalm_getter):

        """
        Function makes a NAPALM call, sends configuration data to merge it with the
        running configuration on a device

        :param napalm_getter: (str) String equal to the NAPALM getter method
        """

        driver = get_network_driver("ios")

        try:  # Telnet connection
            device = driver(
                hostname=self.ip,
                username=self.user,
                password=self.passwd,
                optional_args={"port": 23, "transport": "telnet"},
            )
            device.open()

        except ConnectionException:

            # SSH connection
            device = driver(
                hostname=self.ip,
                username=self.user,
                password=self.passwd,
                optional_args={"port": 22},
            )
            device.open()

        response = eval(napalm_getter)

        device.close()

        date = timestamp()

        return response, date


class GatherInventory(GatherNapalm):

    """
    This class creates an instance that collects general data about a Cisco device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        GatherNapalm.__init__(self, ip, user, passwd)
        self.response, self.date = self.request("device.get_facts()")
        self.dir = "/db/inventory_report"

    def hostname(self):

        """
        Function collects the hostname of a device
        """

        hostname = self.response["hostname"]
        return hostname

    def serial_num(self):

        """
        Function collects the serial number of a device
        """

        sn = self.response["serial_number"]
        return sn

    def version_os(self):

        """
        Function collects the Operative System version of a device
        """

        os = self.response["os_version"]
        return os

    def model(self):

        """
        Function collects the model of a device
        """

        model = self.response["model"]
        return model

    def vendor(self):

        """
        Function collects the vendor of a device
        """

        vendor = self.response["vendor"]
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
            "Vendor": self.vendor(),
        }

        # id_db = self.send2db(self.ip,values,self.dir)
        id_db = send2db(self.ip, values, self.dir)

        return values, id_db


class GatherCapacity(GatherNapalm):

    """
    This class creates an instance that collects general data about physical and
    environmental characteristics of a Cisco device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        GatherNapalm.__init__(self, ip, user, passwd)
        self.response, self.date = self.request("device.get_environment()")
        # print(self.response)
        self.dir = "/db/capacity_report"

    def memory_used(self):

        """
        Function collects used RAM memory in MB and percentage
        """

        response = self.response["memory"]

        # Value transformed from Bytes to MBytes
        total_memory = int(response["available_ram"])
        used_memory = int(response["used_ram"])
        # free_memory = total_memory - used_memory
        used_MB = truncate(used_memory / (10**6), 2)
        used_percentage = truncate((used_memory / total_memory) * 100, 1)

        return used_MB, used_percentage

    def cpu_used(self):

        """
        Function collects CPU usage percentage
        """

        response = self.response["cpu"][0]

        # Value in percentage
        used_cpu = str(response["%usage"])

        return used_cpu

    def hdd_used(self):

        """
        Function collects used hard disk in MB and percentage
        """

        # NAPALM getter does not collect this data!!!
        used_MB = "NAPALMnotImplemented"
        used_percentage = "NAPALMnotImplemented"

        return used_MB, used_percentage

    def interfaces_upordown(self):

        """
        Function collects the number of up and down interfaces
        """

        napalm_getter = "device.get_interfaces()"

        response = self.request(napalm_getter)[0]

        number_total = len(response)

        number_up = 0

        for interface, content in response.items():
            # This method has problems, counts VLAN interfaces too!!!
            if ("is_enabled" in content.keys()) and (
                content["is_enabled"] == True
            ):
                number_up = number_up + 1

        number_down = number_total - number_up

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
            "Timestamp": self.date,
        }
        # id_db = self.send2db(self.ip, values, self.dir)
        id_db = send2db(self.ip, values, self.dir)

        return values, id_db

