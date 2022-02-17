from ncclient import manager
from utils import createPathBackup, createNameBackup, stripTagXml
import xml.dom.minidom



def backupNetconf(ip,user,passwd):


    with manager.connect(host=ip, port='830', username=user,
                        password=passwd, device_params={'name':'csr'}, hostkey_verify=False) as m:

        print(m.connected)
        config = m.get_config('running')
    
    path = createPathBackup()
    filename =  createNameBackup(ip)

    #creating and copying config as string to file
    with open(path+filename+'.xml', 'w') as f:
        f.write(str(config))

    #parsing file with xml.dom.minidom and pretty printing the xml string to the file
    dom = xml.dom.minidom.parse(path+filename+'.xml')
    pretty_xml_as_string = dom.toprettyxml()
    with open(path+filename+'.xml', 'w') as f:
        f.write(pretty_xml_as_string)

    stripTagXml(path+filename+'.xml')



def restoreNetconf(file,ip,user,passwd):

    payload = open(file).read()

    with manager.connect(host=ip, port='830', username=user,
                        password=passwd, device_params={'name':'csr'}, hostkey_verify=False) as m:

        print(m.connected)
        m.edit_config(payload, target="running")
    