from ncclient import manager
import xmltodict
import reporting.constants

device_list = ['172.16.1.2','172.16.1.254','10.0.0.2']
user = 'giguerra'
passwd = 'cisco'

#filter1 = constants.filter

filter2 = open("filter.xml").read()

with manager.connect(host=device_list[1], port='830', username=user,password=passwd, device_params={'name':'csr'}, hostkey_verify=False) as m:

#with manager.connect(host='sandbox-iosxe-recomm-1.cisco.com', port='830', username='developer',password='C1sco12345', device_params={'name':'csr'}, hostkey_verify=False) as m:

    #for capabilitites in m.server_capabilities:
    #        print(capabilitites)

        response = m.get(filter2)

        #response = m.get_schema('Cisco-IOS-XE-native')
        #response = m.get_schema('openconfig-platform')


print(response)
