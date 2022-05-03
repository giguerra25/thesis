import datetime, os
from pathlib import Path
import xmltodict
from apiros.routeros_api import Api as api_ros
import ssl
import math
import xml.etree.cElementTree as ET
import yaml
from netmiko import ConnectHandler
from tinydb import TinyDB


def create_pathdir(dir):
    """
    Function returns the path of a directory.
    if it does not exist the directories, it creates them.

    :param dir: (str) Path of the directory to be created "/path/to/dir".
    """

    pwd = os.getcwd()

    try:
        os.stat(pwd + dir)

    except:
        Path(pwd + dir).mkdir(parents=True, exist_ok=True)

    # It gives full permissions to tftp Mikrotik users
    Path(pwd + dir).chmod(mode=0o777)

    return pwd + dir + "/"


def createPathBackup(ip):

    """
    Function creates directory named after the IP of a device for saving backups.
    It returns the path of the directory created.
    Example /.../files/backups/192.168.1.1/

    :param ip: (str) IP address of the device
    """

    path = create_pathdir("/files/backups/" + ip)

    return path


def createNameBackup(ip, method):

    """
    Function creates a filename composed of ip, timestamp, and management interface used.
    Example: 192.168.1.1_2022-04-27_20:44:31napalm

    :param ip: (str) IP address of the device
    :param method: (str) MGMT interface used. Options [napalm, netconf, apissl, restapi]
    """

    date = datetime.datetime.now().strftime("%d-%m-%-y_%H:%M")
    name = ip + "_" + date + "_" + method
    return name


def timestamp():

    """
    Function creates a timestamp
    """

    date = datetime.datetime.now().strftime("%d-%m-%-y_%H:%M")

    return date


def send2db(ip, record, dir):

    """
    Function sends data to the JSON file (database) related to a device and returns
    the record ID

    :param ip: (str) IP address of the device
    :param record: (str) data to be saved into the JSON file
    :param dir: (str) Path where exists the directory that has the JSON file
    """

    path = create_pathdir(dir)
    db = TinyDB("{}{}.json".format(path, ip))
    id = db.insert(record)

    return id


def stripTagXml(file):

    """
    Function strips two outer tags from the a file with a RPC reply <get-config>

    :param file: (str) The path of the file
    """

    # remove first line with tag <?xml version="1.0" encoding="UTF-8"?>
    # and remove second and last line with tag <rpc-reply>
    with open(file, "r") as fin:
        data = fin.read().splitlines(True)
    with open(file, "w") as fout:
        fout.writelines(data[2:-1])

    # convert xml to dict to change tag <data> for tag <config>
    fileptr = open(file)
    xml_content = fileptr.read()
    file_dict = xmltodict.parse(xml_content)
    data_dict = dict(file_dict)
    data_dict["config"] = data_dict.pop("data")
    # print(data_dict)

    # convert dict to xml and write it into a file
    config_xml = xmltodict.unparse(data_dict, pretty=True)
    with open(file, "w") as f:
        f.write(config_xml)

    # remove first line with tag <?xml version="1.0" encoding="UTF-8"?>
    with open(file, "r") as fin:
        data = fin.read().splitlines(True)
    with open(file, "w") as fout:
        fout.writelines(data[1:])



def rosApi(ip, username, password, api_commands):

    """
    Function to connect via api-ssl to a MikroTik device and make APISSL requests

    :param ip: (str) IP address of the device
    :param username: (str) username on the device with read/write privileges
    :param password: (str)
    :param api_commands: (str, tuple, list) API words that go in the API request

    Example of api_commands:

    string = '/interface/bridge/port/add\n=bridge=bridge1\n=interface=eth3\n=pvid=150'
    tuple = ('/interface/bridge/port/add','=bridge=bridge1','=interface=ether4', '=pvid=150')
    list = ['/interface/bridge/port/add\n=bridge=bridge1\n=interface=eth3\n=pvid=150',
            '/interface/bridge/port/add\n=bridge=bridge1\n=interface=eth4\n=pvid=120']
    """

    # IF device uses API-SSL with certificate
    try:
        router = api_ros(
            ip, user=username, password=password, use_ssl=True
        )
    # If device uses API-SSL without a certificate
    # more info here https://wiki.mikrotik.com/wiki/Manual:API-SSL
    except ssl.SSLError:

        # other solution here https://github.com/socialwifi/RouterOS-api/issues/35
        context = ssl.create_default_context()
        context.check_hostname = False
        context.set_ciphers("ADH:@SECLEVEL=0")

        router = api_ros(
            ip, user=username, password=password, use_ssl=True, context=context
        )

    # try:
    data_dict = router.talk(api_commands)
    return data_dict
    # except:  #if feature was not implemented on routeros_api
    #    data_dict = 'NotImplemented'
    #    return data_dict


def truncate(number, decimals=0):

    """
    Returns a value truncated to a specific number of decimal places.

    :param number: (float)
    :param decimals: (int)
    """

    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0**decimals
    return math.trunc(number * factor) / factor


def xmltree_tag(xml_string, tag):

    """
    Function that walks through an XML tree looking for a node with an specific tag
    It returns the content (text) inside the tag

    :param xml_string: (str) The XML object in string format
    :param tag: (str) The tag of an XML node
    """

    from reporting.constants import tags

    # tree = ET.parse(xml)
    # root = tree.getroot()
    root = ET.fromstring(xml_string)

    for descendant in root.iter(tags[tag]):

        text = descendant.text

    return text


def xmltree_core(xml_string):

    """
    It is special function to count the number of CPU cores in a Cisco device using
    the '{http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper}name"' tag in NETCONF

    It returns a dictionary with: keys -  name of CPU cores
                                  values - percentage of use of each CPU core

    :param xml_string: (str) The XML object in string format
    """

    from reporting.constants import tags

    root = ET.fromstring(xml_string)

    name_cores = []
    perc_use = []
    # loop for device with multiple cores
    for descendant in root.iter(tags["cpu_used"]["cpu_used_corename"]):
        name_cores.append(descendant.text)
    for descendant in root.iter(tags["cpu_used"]["cpu_used_coreidle"]):
        use = str(truncate(100 - float(descendant.text), 2))
        perc_use.append(use)

    dict_cores = {}
    j = 0
    # Dictionary with key as name of CPU core, value as percentage of use
    for i in name_cores:
        dict_cores[i] = perc_use[j]
        j = j + 1

    # print(name_cores)
    # print(perc_use)
    # print(dict_cores)

    return dict_cores


def xmltree_countupdown(xml_string):

    """
    It is special function to count the number of interfaces in a Cisco device using
    the '"{http://openconfig.net/yang/interfaces}enabled"' tag in NETCONF

    It returns a 2-value tuple with: number of interfaces enabled,
                                     number of interfaces disabled

    :param xml_string: (str) The XML object in string format
    """

    from reporting.constants import tags

    root = ET.fromstring(xml_string)

    if_up = 0
    if_total = 0
    for descendant in root.iter(tags["interfaces_enable"]):
        if_total = if_total + 1
        if descendant.text == "true":
            if_up = if_up + 1

    if_down = if_total - if_up

    return if_up, if_down


def readfile_devices():

    """
    Function reads the YAML file with devices' information. It returns a dictionary
    """

    file = input("\nPath to file: ")

    with open(file) as fh:

        dictionary_data = yaml.safe_load(fh)

    return dictionary_data


def ports_mgmt(data=dict):

    """
    Function collects the MGMT interface ports inside the device dictionary

    :param data: (dict) A dicitonary with device information
    """

    ports = {}
    ports["ssh_port"] = data.get("ssh_port")
    ports["netconf_port"] = data.get("netconf_port")
    ports["api-ssl_port"] = data.get("api-ssl_port")
    ports["www-ssl_port"] = data.get("www-ssl_port")

    return ports


def netmikoconfig(ip, user, passwd, commands: list):

    """
    Function sends a list of commands to a Cisco IOS device using Netmiko library
    """

    device = {
        "device_type": "cisco_ios",
        "ip": ip,
        "username": user,
        "global_delay_factor": 2,
        "password": passwd,
    }

    net = ConnectHandler(**device)
    output = net.send_config_set(commands)
    return output


def show_backups(ip):

    """
    FUnction return a list with the backup files for the respective
    device identified with its IP under dir /backup_config

    :param ip: (str) IP address of the device
    """
    pwd = os.getcwd()
    dir = pwd + "/files/backups/" + ip
    file_list = []
    for file in os.listdir(dir):
        file_list.append(file)

    return file_list

