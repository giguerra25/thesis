from backup_restore.backup_cisco_napalm import backupNapalm, restoreNapalm
from backup_restore.backup_cisco_netconf import backupNetconf, restoreNetconf
from backup_restore.backup_mikrotik_rest import backupRestApi, restoreRestApi
from backup_restore.backup_mikrotik_api import backupSSLApi, restoreSSLApi
from reporting.gather_mikrotik_rest import (
    GatherInventory as gatherMikrotikInventoryRest,
)
from reporting.gather_mikrotik_rest import (
    GatherCapacity as gatherMikrotikCapacityRest,
)
from reporting.gather_mikrotik_api import (
    GatherInventory as gatherMikrotikInventoryApi,
)
from reporting.gather_mikrotik_api import (
    GatherCapacity as gatherMikrotikCapacityApi,
)
from reporting.gather_cisco_netconf import (
    GatherInventory as gatherCiscoInventoryNetconf,
)
from reporting.gather_cisco_netconf import (
    GatherCapacity as gatherCiscoCapacityNetconf,
)
from reporting.gather_cisco_napalm import (
    GatherInventory as gatherCiscoInventoryNapalm,
)
from reporting.gather_cisco_napalm import (
    GatherCapacity as gatherCiscoCapacityNapalm,
)
import configuration.config_cisco_napalm
import configuration.config_mikrotik_api
import configuration.config_cisco_netconf
import configuration.config_mikrotik_rest


def backup_cisco(ip, username, passwd, ports):

    """
    Function selects one management interface [NETCONF, CLI] to make backup of a
    Cisco device.

    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param passwd: (str)
    :param ports: (list) Port numbers the device has. [22 for SSH, 830 for NETCONF]
    """

    print("backup Cisco")

    if isinstance(ports["netconf_port"], int):
        print("using NETCONF for backup")
        backupNetconf(ip, username, passwd)
        return

    if isinstance(ports["ssh_port"], int):
        print("using NAPALM for backup")
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

    print("backup MikroTik")

    if isinstance(ports["www-ssl_port"], int):
        print("using REST API for backup")
        backupRestApi(ip, username, passwd)
        return

    if isinstance(ports["api-ssl_port"], int):
        print("using API for backup")
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

    print("restoring Cisco")

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

    print("restoring MikroTik")

    if isinstance(ports["www-ssl_port"], int):

        print("using REST API to restore")
        restoreRestApi(file, ip, username, passwd)
        return

    if isinstance(ports["api-ssl_port"], int):

        print("using API to restore")
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

    print("configuring Cisco")
    
    if type == "static":

        if isinstance(ports["netconf_port"], int):
            print("using NETCONF to configure")
            configuration.config_cisco_netconf.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["ssh_port"], int):
            print("using NAPALM to configure")
            configuration.config_cisco_napalm.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return

    if type == "interface":

        if isinstance(ports["netconf_port"], int):
            print("using NETCONF to configure")
            configuration.config_cisco_netconf.ConfigInterface(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["ssh_port"], int):
            print("using NAPALM to configure")
            configuration.config_cisco_napalm.ConfigInterface(
                ip, username, passwd, config_data
            )
            return

    if type == "vlans":

        if isinstance(ports["ssh_port"], int):
            print("using NAPALM to configure")
            configuration.config_cisco_napalm.ConfigVlan(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["netconf_port"], int):
            print("using NETCONF to configure")
            configuration.config_cisco_netconf.ConfigVlan(
                ip, username, passwd, config_data
            )
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
    
    print("configuring MikroTik")
    
    if type == "static":

        if isinstance(ports["www-ssl_port"], int):
            print("using REST API to configure")
            configuration.config_mikrotik_rest.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["api-ssl_port"], int):
            print("using API to configure")
            configuration.config_mikrotik_api.ConfigStaticRoute(
                ip, username, passwd, config_data
            )
            return

    if type == "interface":

        if isinstance(ports["www-ssl_port"], int):
            print("using REST API to configure")
            configuration.config_mikrotik_rest.ConfigInterface(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["api-ssl_port"], int):
            print("using API to configure")
            configuration.config_mikrotik_api.ConfigInterface(
                ip, username, passwd, config_data
            )
            return

    if type == "vlans":

        if isinstance(ports["www-ssl_port"], int):
            print("using REST API to configure")
            configuration.config_mikrotik_rest.ConfigVlan(
                ip, username, passwd, config_data
            )
            return
        if isinstance(ports["api-ssl_port"], int):
            print("using API to configure")
            configuration.config_mikrotik_api.ConfigVlan(
                ip, username, passwd, config_data
            )
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

    print("gathering Cisco data")

    if type == "inventory":

        if isinstance(ports["netconf_port"], int):
            print("using NETCONF to collect")
            gatherCiscoInventoryNetconf(ip, username, passwd).inventory_dict()
            return

        if isinstance(ports["ssh_port"], int):
            print("using NAPALM to collect")
            gatherCiscoInventoryNapalm(ip, username, passwd).inventory_dict()
            return

    elif type == "capacity":

        if isinstance(ports["netconf_port"], int):
            print("using NETCONF to collect")
            gatherCiscoCapacityNetconf(ip, username, passwd).capacity_dict()
            return

        if isinstance(ports["ssh_port"], int):
            print("using NAPALM to collect")
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

    print("gathering MikroTik data")

    if type == "inventory":

        if isinstance(ports["www-ssl_port"], int):
            print("using REST API to collect")
            gatherMikrotikInventoryRest(ip, username, passwd).inventory_dict()
            return

        if isinstance(ports["api-ssl_port"], int):
            print("using API to collect")
            gatherMikrotikInventoryApi(ip, username, passwd).inventory_dict()
            return

    elif type == "capacity":

        if isinstance(ports["www-ssl_port"], int):
            print("using REST API to collect")
            gatherMikrotikCapacityRest(ip, username, passwd).capacity_dict()
            return

        if isinstance(ports["api-ssl_port"], int):
            print("using API to collect")
            gatherMikrotikCapacityApi(ip, username, passwd).capacity_dict()
            return
