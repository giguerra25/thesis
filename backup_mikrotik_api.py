from utils import rosApi, createNameBackup, createPathBackup
import os



def backupSSLApi(ip,user,passwd):

    """
    Function makes API SSL calls, creates a backup file in the device, 
    collects the backup file in the server, and erases the file in the device.

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    # Creation of a file .backup on the device with API SSL call
    filename =  createNameBackup(ip,'apissl')
    api_command = ('/system/backup/save', '=name='+filename)
    response = rosApi(ip,user,passwd,api_command)
    

    #Collection of the content of the file .backup created.
    path = createPathBackup(ip)
    
    api_command = (
        "/tool/fetch",
        "=upload=yes", 
        "=url=sftp://172.16.1.1"+path+filename+".backup",
        "=user=tftp",
        "=password=tftp",
        "=src-path="+filename+".backup"
        )

    response = rosApi(ip,user,passwd,api_command)
    print(response)

    
    #Checking Finished status in API response
    status = 0
    for element in response:
        if 'status' in element.keys() and element['status']=='finished':
            status = 200

    if status != 200:
        print(response) # error from routeros_api
        print('error getting backup of the device')
        return
    
    #Deleting file .backup created on device
    else: 
        #Find ID of backup file
        api_command = ('/file/print')
        response = rosApi(ip,user,passwd,api_command)
        id_file = ''
        for element in response:
            if 'name' in element.keys() and element['name']==filename+".backup":
                id_file = element['.id']

        print('deleting backup on device')
        api_command = ('/file/remove', '=.id='+id_file)
        response = rosApi(ip,user,passwd,api_command)
        print(response)


def restoreSSLApi(file,ip,user,passwd):

    """
    Function makes an API SSL call, sends a .backup file to a device, and loads
    the .backup file into the device.

    :param file: (str) Path to the file with the configuration
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """
    
    path = os.path.dirname(file) # CHECK IF THIS IS NEEDED
    filename = os.path.basename(file)

    # API request to get file .backup to device via SFTP
    api_command = (
        "/tool/fetch",
        "=url=sftp://172.16.1.1"+file,
        "=user=tftp",
        "=password=tftp",
        "=dst-path="+filename
        )
    
    response = rosApi(ip,user,passwd,api_command)
    print(response)
    #[{'status': 'connecting', '.section': '0'}, {'status': 'connecting', '.section': '1'}, {'status': 'finished', 'downloaded': '14', 'total': '14', 'duration': '1s', '.section': '2'}]

    # API request to execute file .backup on device
    api_command = ('/system/backup/load', '=name='+filename)
    response = rosApi(ip,user,passwd,api_command)
    print(response)
