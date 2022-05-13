import requests
import os
from requests.auth import HTTPBasicAuth
import json
from utils import createPathBackup, createNameBackup


def backupRestApi(ip, user, passwd):

    """
    Function makes REST API calls, creates a backup file in the device,
    collects the backup file in the server, and erases the file in the device.

    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    url = "https://" + ip + "/rest"

    filename = createNameBackup(ip, "restapi")

    
    # Creation of a file .backup on the device with REST API call
    data = {"name": filename}

    response = requests.post(
        url + "/system/backup/save",
        auth=HTTPBasicAuth(user, passwd),
        data=json.dumps(data),
        verify=False,
    )

    # Collection of the content of the file .backup created with REST API call
    path = createPathBackup(ip)

    data = {
        "upload": "yes",
        "url": "sftp://172.16.1.1" + path + filename + ".backup",
        "user": "tftp",
        "password": "tftp",
        "src-path": filename + ".backup",
    }

    response = requests.post(
        url + "/tool/fetch",
        auth=HTTPBasicAuth(user, passwd),
        data=json.dumps(data),
        verify=False,
    )

    # Checking Error status in API response
    if response.status_code != 200:

        print(response.status_code)  # code 400
        print("error getting backup of the device")
        return

    # Deleting file .backup created on device
    else:

        print("deleting backup on device")

        requests.delete(
            url + "/file/" + filename + ".backup",
            auth=HTTPBasicAuth(user, passwd),
            verify=False,
        )



def restoreRestApi(file, ip, user, passwd):

    """
    Function makes REST API calls, sends a .backup file to a device, and loads
    the .backup file into the device.

    :param file: (str) Path to the file with the configuration
    :param ip: (str) IP address of the device
    :param user: (str) username on the device with read/write privileges
    :param passwd: (str)
    """

    url = "https://" + ip + "/rest"

    path = os.path.dirname(file)  # CHECK IF THIS IS NEEDED
    filename = os.path.basename(file)

    # POST request to get file .backup to device via SFTP
    data = {
        "url": "sftp://172.16.1.1{}".format(file),
        "user": "tftp",
        "password": "tftp",
        "dst-path": filename,
    }

    response = requests.post(
        url + "/tool/fetch",
        auth=HTTPBasicAuth(user, passwd),
        data=json.dumps(data),
        verify=False,
    )

    # print(json.dumps(response.json(), indent=4))  # prints progress upload file to device

    # POST request to execute file .backup on device
    data = {
        "name": filename,
    }

    response = requests.post(
        url + "/system/backup/load",
        auth=HTTPBasicAuth(user, passwd),
        data=json.dumps(data),
        verify=False,
    )

    #print(json.dumps(response.json(), indent=4)) # prints empty []
