# from utils import readfile_devices, ports_mgmt, show_backups
from backup_cisco_napalm import backupNapalm, restoreNapalm
from backup_cisco_netconf import backupNetconf, restoreNetconf
from backup_mikrotik_rest import backupRestApi, restoreRestApi
from backup_mikrotik_api import backupSSLApi, restoreSSLApi
from gather_mikrotik_rest import GatherInventory as gatherMikrotikInventoryRest
from gather_mikrotik_rest import GatherCapacity as gatherMikrotikCapacityRest
from gather_mikrotik_api import GatherInventory as gatherMikrotikInventoryApi
from gather_mikrotik_api import GatherCapacity as gatherMikrotikCapacityApi
from gather_cisco_netconf import GatherInventory as gatherCiscoInventoryNetconf
from gather_cisco_netconf import GatherCapacity as gatherCiscoCapacityNetconf
from gather_cisco_napalm import GatherInventory as gatherCiscoInventoryNapalm
from gather_cisco_napalm import GatherCapacity as gatherCiscoCapacityNapalm
# from report_maker import Report
import config_cisco_napalm
import config_mikrotik_api
import config_cisco_netconf
import config_mikrotik_rest
# import os



def backup_cisco(ip, username, passwd, ports):

    """
    Function selects one management interface [NETCONF, CLI] to make backup of a
    Cisco device.

    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has. [22 for SSH, 830 for NETCONF]
    """

    print("backup cisco")

    if isinstance(ports["netconf_port"], int):

        backupNetconf(ip, username, passwd)
        return

    if isinstance(ports["ssh_port"], int):

        backupNapalm(ip, username, passwd)
        return


def backup_mikrotik(ip, username, passwd, ports):

    """
    Function selects one management interface [REST API, SSL API] to make backup of a
    MikroTik device.

    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has [22 for SSH, 443 for REST API, 8729 for SSL API]
    """

    print("backup mikrotik")

    if isinstance(ports["www-ssl_port"], int):

        backupRestApi(ip, username, passwd)
        return

    if isinstance(ports["api-ssl_port"], int):

        backupSSLApi(ip, username, passwd)
        return


def restore_backup_cisco(file, ip, username, passwd, ports):

    """
    Function selects one management interface [NETCONF, CLI] to restore
    configuration in a Cisco device.

    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has. [22 for SSH, 830 for NETCONF]
    """

    print("restoring cisco")

    if isinstance(ports["netconf_port"], int):

        print("using NETCONF to restore")
        restoreNetconf(file, ip, username, passwd)
        return

    if isinstance(ports["ssh_port"], int):

        print("using NAPALM to restore")
        restoreNapalm(file, ip, username, passwd)
        return


def restore_backup_mikrotik(file, ip, username, passwd, ports):

    """
    Function selects one management interface [REST API, SSL API] to restore
    configuration in a MikroTik device.

    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has [22 for SSH, 443 for REST API, 8729 for SSL API]
    """

    print("restoring mikrotik")

    if isinstance(ports["www-ssl_port"], int):

        restoreRestApi(file, ip, username, passwd)
        return

    if isinstance(ports["api-ssl_port"], int):

        restoreSSLApi(file, ip, username, passwd)
        return


def config_cisco(type, ip, username, passwd, config_data, ports):

    """
    Function selects one management interface [NETCONF, CLI] to make a
    configuration in a Cisco device.

    :param type: (str) String indicates what configurations will be done
    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has. [22 for SSH, 830 for NETCONF]
    """

    if type == "static":

        if isinstance(ports["netconf_port"], int):
            config_cisco_netconf.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["ssh_port"], int):
            config_cisco_napalm.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return

    if type == "interface":

        if isinstance(ports["netconf_port"], int):
            config_cisco_netconf.ConfigInterface(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["ssh_port"], int):
            config_cisco_napalm.ConfigInterface(
                ip, username, passwd, config_data
            )
            return

    if type == "vlans":

        if isinstance(ports["ssh_port"], int):
            config_cisco_napalm.ConfigVlan(ip, username, passwd, config_data)
            return
        if isinstance(ports["netconf_port"], int):
            config_cisco_netconf.ConfigVlan(ip, username, passwd, config_data)
            return


def config_mikrotik(type, ip, username, passwd, config_data, ports):

    """
    Function selects one management interface [REST API, SSL API] to make a
    configuration in a MikroTik device.

    :param type: (str) String indicates what configurations will be done
    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has [22 for SSH, 443 for REST API, 8729 for SSL API]
    """

    if type == "static":

        if isinstance(ports["www-ssl_port"], int):
            config_mikrotik_rest.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["api-ssl_port"], int):
            config_mikrotik_api.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return

    if type == "interface":

        if isinstance(ports["www-ssl_port"], int):
            config_mikrotik_rest.ConfigInterface(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["api-ssl_port"], int):
            config_mikrotik_api.ConfigInterface(
                ip, username, passwd, config_data
            )
            return

    if type == "vlans":

        if isinstance(ports["www-ssl_port"], int):
            config_mikrotik_rest.ConfigVlan(ip, username, passwd, config_data)
            return
        if isinstance(ports["api-ssl_port"], int):
            config_mikrotik_api.ConfigVlan(ip, username, passwd, config_data)
            return


def gathering_cisco(type, ip, username, passwd, ports):

    """
    Function selects one management interface [NETCONF, CLI] to collect data from a
    Cisco device.

    :param type: (str) String indicates what data will be collected
    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has. [22 for SSH, 830 for NETCONF]
    """

    print("gathering data cisco")

    if type == "inventory":

        if isinstance(ports["netconf_port"], int):

            gatherCiscoInventoryNetconf(ip, username, passwd).inventory_dict()
            return

        if isinstance(ports["ssh_port"], int):

            gatherCiscoInventoryNapalm(ip, username, passwd).inventory_dict()
            return

    elif type == "capacity":

        if isinstance(ports["netconf_port"], int):

            gatherCiscoCapacityNetconf(ip, username, passwd).capacity_dict()
            return

        if isinstance(ports["ssh_port"], int):

            gatherCiscoCapacityNapalm(ip, username, passwd).capacity_dict()
            return


def gathering_mikrotik(type, ip, username, passwd, ports):

    """
    Function selects one management interface [REST API, SSL API] to collect data from
    a MikroTik device.

    :param type: (str) String indicates what data will be collected
    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has [22 for SSH, 443 for REST API, 8729 for SSL API]
    """

    print("gathering data mikrotik")

    if type == "inventory":

        if isinstance(ports["www-ssl_port"], int):

            gatherMikrotikInventoryRest(ip, username, passwd).inventory_dict()
            return

        if isinstance(ports["api-ssl_port"], int):

            gatherMikrotikInventoryApi(ip, username, passwd).inventory_dict()
            return

    elif type == "capacity":

        if isinstance(ports["www-ssl_port"], int):

            gatherMikrotikCapacityRest(ip, username, passwd).capacity_dict()
            return

        if isinstance(ports["api-ssl_port"], int):

            gatherMikrotikCapacityApi(ip, username, passwd).capacity_dict()
            return