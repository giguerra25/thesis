from utils import rosApi, truncate, timestamp, send2db


class GatherApi:

    """
    This is the base class we have to inherit from when writing data gathering
    features for MikroTik devices based on API SSL

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd

    def request(self, api_command):

        """
        Function makes an API SSL request, sends an API word to gather data
        from a device

        :param api_command: (str) API word
        """

        response = rosApi(self.ip, self.user, self.passwd, api_command)

        date = timestamp()

        return response, date


class GatherInventory(GatherApi):

    """
    This class creates an instance that collects general data about a MikroTik device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        GatherApi.__init__(self, ip, user, passwd)
        self.response, self.date = self.request("/system/resource/print")
        self.dir = "/db/inventory_report"
        # print(self.response)

    def hostname(self):

        """
        Function collects the hostname of a device
        """

        resource = "/system/identity/print"

        # response = ([{'name': 'R1changed'}], '2022-04-12_11:47:09')
        response = self.request(resource)[0][0]
        hostname = response["name"]
        return hostname

    def serial_num(self):

        """
        Function collects the serial number of a device
        """

        resource = "/system/license/print"
        response = self.request(resource)[0][0]
        sn = response["system-id"]
        return sn

    def version_os(self):

        """
        Function collects the Operative System version of a device
        """

        os = self.response[0]["version"]
        return os

    def model(self):

        """
        Function collects the model of a device
        """

        model = self.response[0]["board-name"]
        return model

    def vendor(self):

        """
        Function collects the vendor of a device
        """

        vendor = self.response[0]["platform"]
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


class GatherCapacity(GatherApi):

    """
    This class creates an instance that collects general data about physical and
    environmental characteristics of a MikroTik device

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    def __init__(self, ip, user, passwd):
        GatherApi.__init__(self, ip, user, passwd)
        self.response, self.date = self.request("/system/resource/print")
        self.dir = "/db/capacity_report"

    def memory_used(self):

        """
        Function collects used RAM memory in MB and percentage
        """

        response = self.response[0]

        # Value transformed from Bytes to MBytes
        free_memory = int(response["free-memory"])
        total_memory = int(response["total-memory"])
        used_memory = total_memory - free_memory
        used_MB = truncate(used_memory / (10**6), 2)
        used_percentage = truncate((used_memory / total_memory) * 100, 1)

        return used_MB, used_percentage

    def cpu_used(self):

        """
        Function collects CPU usage percentage
        """

        response = self.response[0]

        # Value in percentage
        used_cpu = str(response["cpu-load"])

        return used_cpu

    def hdd_used(self):

        """
        Function collects used hard disk in MB and percentage
        """

        response = self.response[0]

        # Value transformed from Bytes to MBytes
        free_hdd = int(response["free-hdd-space"])
        total_hdd = int(response["total-hdd-space"])
        used_hdd = total_hdd - free_hdd
        used_MB = truncate(used_hdd / (10**6), 2)
        used_percentage = truncate((used_hdd / total_hdd) * 100, 1)

        return used_MB, used_percentage

    def interfaces_upordown(self):

        """
        Function collects the number of up and down interfaces
        """

        resource = "/interface/ethernet/print"

        response = self.request(resource)[0]

        number_total = len(response)

        number_up = 0

        for interface in response:
            if ("disabled" in interface) and (
                interface["disabled"] == "false"
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

