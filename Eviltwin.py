from scapy.all import srp , Ether , ARP , arping , IFACES , get_if_addr
from os import system
from Misc import *

def print_connected_devices(net_ip:str , MACDB, interface):
	print("clearing ARP cache...")
	os.system("ip neigh flush all")

	target = get_netaddr(net_ip,"24")
	ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=target) , timeout = 3 , iface = interface , inter = 0.05)

	print("\n")

	clients = []

	for sent , received in ans :
		clients.append({ "ip" : received.psrc , "mac" : received.hwsrc})

	print("Connected devices :")
	for c in clients :
		print ("{:16}	{:16}	{}".format(  c["ip"], c["mac"] , MAC_to_vendor( c["mac"].upper() , MACDB)    ))
	return clients

def start_hotspot(SSID:str , interface , con_name="WCHECK-CONNECTION"):
	os.system("nmcli con add type wifi ifname "+interface+" con-name "+ con_name +" ssid \""+SSID+"\"")
	os.system("nmcli con modify " + con_name + " 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared")
	os.system("nmcli con up "+con_name)

def stop_hotspot(con_name="WCHECK-CONNECTION"):
	os.system("nmcli con down " + con_name)
	os.system("nmcli con delete " + con_name)

