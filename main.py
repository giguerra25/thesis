from simple_term_menu import TerminalMenu
from utils import readfile_devices, ports_mgmt, show_backups
from reporting.report_maker import Report
import os
from selector import (
    backup_cisco,
    backup_mikrotik,
    restore_backup_cisco,
    restore_backup_mikrotik,
    config_cisco,
    config_mikrotik,
    gathering_cisco,
    gathering_mikrotik,
)


# requests.exceptions.SSLError: HTTPSConnectionPool(host='10.0.0.6', port=443): Max retries exceeded with url: /rest/system/resource (Caused by SSLError(SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure (_ssl.c:1131)')))
from requests.exceptions import SSLError

# ncclient.transport.errors.SSHError: Could not open socket to 172.16.1.2:830
from ncclient.transport.errors import SSHError


def main():

    # STRINGS USED ON MENU AND SUBMENUS
    TITLE = """\nNET_TOOL\n 
    Scripts for Network Automation on Cisco and MikroTik\n"""
    SUBTITLE1 = "\nTypes of reports\n"
    SUBTITLE2 = "\nTypes of configurations\n"

    ITEM_BACKUP = "Make a backup from a device(s)"
    ITEM_RESTORE = "Restore a device(s) with a backup"
    ITEM_REPORT = "Create a report from a device(s)"
    ITEM_CONFIG = "Make new configurations on a device(s)"

    REPORT_TYPE_1 = "Inventory"
    REPORT_TYPE_2 = "Capacity"

    TYPE_CONFIG_1 = "Configure IP static routes"
    TYPE_CONFIG_2 = "Configure interfaces"
    TYPE_CONFIG_3 = "Configure VLANs"

    main_menu = [
        "[a] " + ITEM_BACKUP,
        "[b] " + ITEM_RESTORE,
        "[c] " + ITEM_REPORT,
        "[d] " + ITEM_CONFIG,
        "[q] quit",
    ]

    sub_menu1 = [
        "[a] " + REPORT_TYPE_1, 
        "[b] " + REPORT_TYPE_2, 
        "[d] go back",
    ]

    sub_menu2 = [
        "[a] " + TYPE_CONFIG_1,
        "[b] " + TYPE_CONFIG_2,
        "[c] " + TYPE_CONFIG_3,
        "[d] go back",
    ]

    terminal_menu = TerminalMenu(main_menu, title=TITLE)
    terminal_submenu1 = TerminalMenu(sub_menu1, title=SUBTITLE1)
    terminal_submenu2 = TerminalMenu(sub_menu2, title=SUBTITLE2)

    # MAIN MENU
    # the letter in the square brackets too can use to index the options
    loop = True
    while loop:
        choice = main_menu[terminal_menu.show()]

        # BACKUP
        if choice == main_menu[0]:

            list_devices = readfile_devices()

            # Make backup sequentially for every device
            for device in list_devices:

                ip = device["mgmt_ip"]
                username = device["username"]
                passwd = device["password"]
                vendor = device["vendor"]
                ports = ports_mgmt(device)

                if vendor in ("Cisco", "CISCO", "cisco"):

                    backup_cisco(ip, username, passwd, ports)

                elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                    backup_mikrotik(ip, username, passwd, ports)

            # loop = False

        # RESTORE
        elif choice == main_menu[1]:

            list_devices = readfile_devices()

            # Make restore sequentially for every device
            for device in list_devices:

                ip = device["mgmt_ip"]
                username = device["username"]
                passwd = device["password"]
                vendor = device["vendor"]
                ports = ports_mgmt(device)

                # Submenu to show backups of the device
                file_list = show_backups(ip)
                file_list.append("go back")
                SUBTITLE3 = "\nOptions for device {}:\n".format(ip)
                terminal_submenu3 = TerminalMenu(file_list, title=SUBTITLE3)

                sub_loop3 = True
                while sub_loop3:
                    choice = file_list[terminal_submenu3.show()]

                    # Selection of a backup file
                    if choice != "go back":

                        pwd = os.getcwd()
                        file = pwd + "/files/backups/" + ip + "/" + choice

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            restore_backup_cisco(
                                file, ip, username, passwd, ports
                            )
                            sub_loop3 = False

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            restore_backup_mikrotik(
                                file, ip, username, passwd, ports
                            )
                            sub_loop3 = False

                    # Exit Restore Submenu
                    elif choice == "go back":
                        sub_loop3 = False

        # REPORTING
        elif choice == main_menu[2]:

            sub_loop1 = True
            while sub_loop1:
                choice = sub_menu1[terminal_submenu1.show()]

                # Inventory report
                if choice == sub_menu1[0]:
                    print(choice)

                    type = "inventory"
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device["mgmt_ip"]
                        username = device["username"]
                        passwd = device["password"]
                        vendor = device["vendor"]
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            gathering_cisco(type, ip, username, passwd, ports)

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            gathering_mikrotik(
                                type, ip, username, passwd, ports
                            )

                        devices_gathered.append(ip)

                    # Report is generated with a list of devices
                    a = Report(devices_gathered, type)
                    a.render_pdfreport()

                # Capacity report
                elif choice == sub_menu1[1]:
                    print(choice)

                    type = "capacity"
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device["mgmt_ip"]
                        username = device["username"]
                        passwd = device["password"]
                        vendor = device["vendor"]
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            gathering_cisco(type, ip, username, passwd, ports)

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            gathering_mikrotik(
                                type, ip, username, passwd, ports
                            )

                        devices_gathered.append(ip)

                    # Report is generated with a list of devices
                    a = Report(devices_gathered, type)
                    a.render_pdfreport()

                # Exit Reporting Submenu
                elif choice == sub_menu1[2]:
                    sub_loop1 = False

        # CONFIGURATION
        elif choice == main_menu[3]:

            sub_loop2 = True
            while sub_loop2:
                choice = sub_menu2[terminal_submenu2.show()]

                # Configure Static routes
                if choice == sub_menu2[0]:
                    print(choice)

                    type = "static"
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device["mgmt_ip"]
                        username = device["username"]
                        passwd = device["password"]
                        vendor = device["vendor"]
                        config_data = device["routes"]
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            config_cisco(
                                type, ip, username, passwd, config_data, ports
                            )

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            config_mikrotik(
                                type, ip, username, passwd, config_data, ports
                            )

                # Configure interfaces
                elif choice == sub_menu2[1]:
                    print(choice)

                    type = "interface"
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device["mgmt_ip"]
                        username = device["username"]
                        passwd = device["password"]
                        vendor = device["vendor"]
                        config_data = device["interfaces"]
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            config_cisco(
                                type, ip, username, passwd, config_data, ports
                            )

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            config_mikrotik(
                                type, ip, username, passwd, config_data, ports
                            )

                # Configure VLANs
                elif choice == sub_menu2[2]:
                    print(choice)

                    type = "vlans"
                    devices_gathered = []

                    list_devices = readfile_devices()

                    for device in list_devices:

                        ip = device["mgmt_ip"]
                        username = device["username"]
                        passwd = device["password"]
                        vendor = device["vendor"]
                        config_data = device["vlans"]
                        ports = ports_mgmt(device)

                        if vendor in ("Cisco", "CISCO", "cisco"):

                            config_cisco(
                                type, ip, username, passwd, config_data, ports
                            )

                        elif vendor in ("Mikrotik", "MIKROTIK", "mikrotik"):

                            config_mikrotik(
                                type, ip, username, passwd, config_data, ports
                            )

                # Exit COnfiguration Submenu
                elif choice == sub_menu2[3]:
                    sub_loop2 = False

        # EXIT MAIN MENU
        elif choice == main_menu[4]:
            loop = False


main()
