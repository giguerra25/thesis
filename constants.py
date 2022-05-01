"""Constants to be used across NETCONF related scripts."""


tags = {

        "hostname":"{http://cisco.com/ns/yang/Cisco-IOS-XE-native}hostname",
        "sn":"{http://cisco.com/ns/yang/Cisco-IOS-XE-native}sn",
        "os":"{http://cisco.com/ns/yang/Cisco-IOS-XE-native}version",
        "model":"{http://cisco.com/ns/yang/Cisco-IOS-XE-native}pid",
        "mem_used_KB":"{http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper}used-number",
        "mem_used_%":"{http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper}used-percent",
        "cpu_used":{
            "cpu_used_corename": "{http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper}name",
            "cpu_used_coreidle": "{http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper}idle",
        },
        "hdd_used_b": "{http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper}used-size",
        "hdd_total_b": "{http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper}total-size",
        "interfaces_enable":"{http://openconfig.net/yang/interfaces}enabled",
    }



filter_hostname = """
<filter>
<native 
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname></hostname>
</native>
</filter>"""


filter_serialnumber = """
<filter>
<native 
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <license>
        <udi>
        <sn></sn>
        </udi>
    </license>
</native>
</filter>"""

filter_osversion = """
<filter>
<native 
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <version></version>
</native>
</filter>"""

filter_model = """
<filter>
<native 
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <license>
        <udi>
        <pid></pid>
        </udi>
    </license>
</native>
</filter>"""


filter_memoryused = """
<filter>
<cisco-platform-software 
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper">
    <control-processes>
        <control-process>
            <memory-stats>
            <used-number></used-number>
            <used-percent></used-percent>
            </memory-stats>
        </control-process>
    </control-processes>
</cisco-platform-software>
</filter>
"""


filter_cpuused = """
<filter>
<cisco-platform-software 
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper">
    <control-processes>
        <control-process>
            <per-core-stats>
                <per-core-stat>
                    <name></name>
                    <idle></idle>
                </per-core-stat>
            </per-core-stats>
        </control-process>
    </control-processes>
</cisco-platform-software>
</filter>
"""


filter_hddused = """
<filter>
<cisco-platform-software 
    xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-platform-software-oper">
    <q-filesystem>
        <partitions>
            <name>bootflash:</name>
            <total-size></total-size>
            <used-size></used-size>
        </partitions>
    </q-filesystem>
</cisco-platform-software>
</filter>
"""

filter_interfacesupdown = """
<filter>
<interfaces 
    xmlns="http://openconfig.net/yang/interfaces">
    <interface>
        <state>
            
            <enabled></enabled>
            <name></name>
        </state>
    </interface>
</interfaces>
</filter>
"""



filter_interfacesipdown2 = """
<filter>
<interfaces-state 
    xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">

    <interface>
        <name></name>
        <admin-status></admin-status>
        <if-index></if-index>
    </interface>

</interfaces-state>
</filter>
"""


filter_serialnumber2 = """
<filter>
<device-hardware-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-device-hardware-oper">
    <device-hardware>
        <device-inventory>
        <serial-number></serial-number>
        </device-inventory>
    </device-hardware>
</device-hardware-data>
</filter>"""



filter_osversion2 = """
<filter>
<device-hardware-data 
xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-device-hardware-oper">
    <device-hardware>
        <device-system-data>
        <software-version></software-version>
        </device-system-data>
    </device-hardware>
</device-hardware-data>
</filter>"""


filter_totalmemory2 = """
<filter>
<memory-statistics xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-memory-oper">
    <memory-statistic>
        <total-memory>
        </total-memory>
    </memory-statistic>
</memory-statistics>
</filter>
"""

filter_usedmemory2 = """
<filter>
<memory-statistics xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-memory-oper">
    <memory-statistic>
        <used-memory>
        </used-memory>
    </memory-statistic>
</memory-statistics>
</filter>
"""


filter_vlan = """
<filter>
<vlans 
    xmlns="http://openconfig.net/yang/openconfig-vlan">

</vlans>
</filter>"""

filter2 = """
<filter>
<memory-statistics xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-memory-oper">

</memory-statistics>
</filter>"""

