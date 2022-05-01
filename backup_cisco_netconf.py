from ncclient import manager
from utils import createPathBackup, createNameBackup, stripTagXml
import xml.dom.minidom



def backupNetconf(ip,user,passwd):

    """
    Function makes a NETCONF RPC call, collects the running configuration data from 
    a device and creates a file with it.

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    # NETCONF RPC call to collect configuration from Cisco IOS device
    with manager.connect(host=ip, 
                        port='830', 
                        username=user,
                        password=passwd, 
                        device_params={'name':'csr'}, 
                        hostkey_verify=False) as m:

        print(m.connected)
        config = m.get_config('running')
    
    path = createPathBackup(ip)
    filename =  createNameBackup(ip,'netconf')

    #creating file with config data in XML
    with open(path+filename+'.xml', 'w') as f:
        f.write(str(config))

    #parsing file with xml.dom.minidom and pretty printing the xml string to the file
    dom = xml.dom.minidom.parse(path+filename+'.xml')
    pretty_xml_as_string = dom.toprettyxml()
    with open(path+filename+'.xml', 'w') as f:
        f.write(pretty_xml_as_string)
    
    # strips outter tags from the XML file
    stripTagXml(path+filename+'.xml')



def restoreNetconf(file,ip,user,passwd):

    """
    Function makes a NETCONF RPC call, sends a file with running configuration data to 
    a device and commits the change.

    :param file: (str) Path to the file with the configuration
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    payload = open(file).read()

    # NETCONF RPC call to send configuration to Cisco IOS device
    with manager.connect(host=ip, 
                        port='830', 
                        username=user,
                        password=passwd, 
                        device_params={'name':'csr'}, 
                        hostkey_verify=False) as m:

        print(m.connected)
        m.edit_config(payload, target="running")
    