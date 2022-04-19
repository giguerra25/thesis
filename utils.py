import datetime, os, shutil
from pathlib import Path
from tracemalloc import Snapshot
import xmltodict
import routeros_api
import ssl
import math
import xml.etree.cElementTree as ET



def create_pathdir(dir): 
    """
    Function returns the path ./db/<report_directory>/ of the directory. 
    if it does not exist, it creates one.
    """

    pwd = os.getcwd()

    try:
        os.stat(pwd+dir)
        
    except:
        Path(pwd+dir).mkdir(parents=True, exist_ok=True)
    
    return pwd + dir + '/'


def createPathBackup():

    path  = create_pathdir('/backup_config')

    return path



def createNameBackup(ip):

    """
    Function returns filename composed of ip and timestamp.
    """

    date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    name = ip + '_' + date
    return name

def stripTagXml(file):

    """
    Function strips two outer tags to fulfill for RPC <edit-config> request
    """

    '''import xml.etree.ElementTree as ET

    tree = ET.parse(file)
    root = tree.getroot()

    print(root.attrib)
    print(root.tag)
    new = ''
    for child in root:
        for subchild in child:
            new += str(subchild)
            print(subchild.tag, subchild.attrib)

    f = open('other.xml', 'w')
    f.write(new)
    f.close()'''

    '''import xml.etree.ElementTree as ET
    tree = ET.parse(file)
    root = tree.getroot()
    root.tag = 'config'
    tree.write(file)'''

    #remove first line with tag <?xml version="1.0" encoding="UTF-8"?>
    # and remove second and last line with tag <rpc-reply>
    with open(file, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(file, 'w') as fout:
        fout.writelines(data[2:-1])
    
    #convert xml to dict to change tag <data> for tag <config>
    fileptr = open(file)
    xml_content= fileptr.read()
    file_dict=xmltodict.parse(xml_content)
    data_dict = dict(file_dict)
    data_dict['config'] = data_dict.pop('data')
    #print(data_dict)

    #convert dict to xml and write it into a file
    config_xml=xmltodict.unparse(data_dict,pretty=True)
    with open(file, 'w') as f:
        f.write(config_xml)

    #remove first line with tag <?xml version="1.0" encoding="UTF-8"?>
    with open(file, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(file, 'w') as fout:
        fout.writelines(data[1:])


#dir = os.getcwd()+'/backup_config/'
#stripTagXml(dir+'R3copy.xml')


def moveFile(src,dst):

    shutil.move(src,dst)



def rosApi(ip,username,password,api_commands):

        
        try:
            router = routeros_api.Api(ip, 
                        user=username, 
                        password=password, 
                        use_ssl=True
            )
            
        except ssl.SSLError:

            context = ssl.create_default_context()  
            context.check_hostname = False
            context.set_ciphers('ADH:@SECLEVEL=0')

            router = routeros_api.Api(ip, 
                        user=username, 
                        password=password, 
                        use_ssl=True, 
                        context=context
            )
            
        try: 
            data_dict = router.talk(api_commands)
            return data_dict
        except:  #if feature was not implemented on routeros_api 
            data_dict = 'NotImplemented'
            return data_dict



def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


def xmltree_tag(xml_string,tag):

    from constants import tags
    #tree = ET.parse(xml)
    #root = tree.getroot()
    root = ET.fromstring(xml_string)

    # loop for device with multiple cores
    """if tag == 'cpu_used':

        name_cores=[]
        perc_use=[]
        for descendant in root.iter(tags[tag]["cpu_used_corename"]):
            name_cores.append(descendant.text)
        for descendant in root.iter(tags[tag]["cpu_used_coreidle"]):
            use = str(truncate(100-float(descendant.text),2))
            perc_use.append(use)
        
        dict_cores={}
        j=0
        for i in name_cores:
            dict_cores[i]=perc_use[j]
            j=j+1

        #print(name_cores)
        #print(perc_use)
        #print(dict_cores)
        return dict_cores"""


    for descendant in root.iter(tags[tag]):
    
        text = descendant.text

    return text


def xmltree_core(xml_string):

    from constants import tags

    root = ET.fromstring(xml_string)

    name_cores=[]
    perc_use=[]
    for descendant in root.iter(tags['cpu_used']["cpu_used_corename"]):
        name_cores.append(descendant.text)
    for descendant in root.iter(tags['cpu_used']["cpu_used_coreidle"]):
        use = str(truncate(100-float(descendant.text),2))
        perc_use.append(use)

    dict_cores={}
    j=0
    for i in name_cores:
        dict_cores[i]=perc_use[j]
        j=j+1

    #print(name_cores)
    #print(perc_use)
    #print(dict_cores)
    return dict_cores


def xmltree_countupdown(xml_string):

    from constants import tags

    root = ET.fromstring(xml_string)

    if_up = 0
    if_total = 0
    for descendant in root.iter(tags["interfaces_enable"]):
        if_total = if_total + 1
        if descendant.text == 'true': if_up = if_up + 1
    
    if_down = if_total - if_up

    return if_up, if_down



#print(xpath_hostname('response.xml'))

