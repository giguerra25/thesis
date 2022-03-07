from utils import ros_api


device_list = ['10.0.0.2','10.0.0.6']
user = 'giguerra'
passwd = 'cisco'

api_commands = '/ip/address/print'

a = ros_api(device_list[1],user,passwd,api_commands)