import datetime, os, shutil
import xmltodict
import routeros_api
import ssl

def createPathBackup(): 
    """
    Function returns the path of the directory to save backups. 
    if it does not exist, it creates one.
    """
    pwd = os.getcwd()

    try:
        os.stat(pwd+'/backup_config')
    except:
        os.mkdir(pwd+'/backup_config')
    
    return pwd + '/backup_config/'


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

