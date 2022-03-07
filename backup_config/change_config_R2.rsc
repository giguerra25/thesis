# mar/02/2022 12:21:53 by RouterOS 7.1
# software id = 
#
/interface bridge
add name=loopback0
/interface ethernet
set [ find default-name=ether1 ] disable-running-check=false
set [ find default-name=ether2 ] disable-running-check=false
set [ find default-name=ether3 ] disable-running-check=false
/disk
set sata1 disabled=false
/interface wireless security-profiles
set [ find default=true ] supplicant-identity=MikroTik
/port
set 0 name=serial0
/routing ospf instance
add name=instance1
/routing ospf area
add instance=instance1 name=backbone
/ip address
add address=10.0.0.2/30 interface=ether1 network=10.0.0.0
add address=2.2.2.2 interface=loopback0 network=2.2.2.2
add address=10.0.0.5/30 interface=ether2 network=10.0.0.4
add address=192.168.50.254/24 interface=ether3 network=192.168.50.0
/ip dhcp-client
add interface=ether1
/ip service
set www-ssl certificate=ServerCA disabled=false
/routing ospf interface-template
add area=backbone interfaces=ether1
add area=backbone interfaces=ether2
/system identity
set name=R2cambiado
