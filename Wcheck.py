from scapy.all import srp , Ether , ARP , arping , IFACES , get_if_addr
import json
import os
import time
from wifi import Cell, Scheme

# Uncomment this to run it from outside of the script's directory.
#os.chdir("/opt/Wcheck")


def init_MAC_DB():
	res = {}
	with open("fMAC_DB.json") as f :
		res = json.load(f)
	return res

def MAC_to_vendor(MAC_prefix:str , MAC_DB:dict) :
	#print("Looking for" , MAC_prefix , " among " , len(MAC_DB), " MAC prefixes...")
	if len(MAC_prefix) < 8 :
		return "Unknown"

	elif MAC_prefix in MAC_DB :
		return MAC_DB[MAC_prefix]["vendorName"]
	else :
		if MAC_prefix[-2] == ':' :
			return MAC_to_vendor(MAC_prefix[:-2] , MAC_DB)
		else :
			return MAC_to_vendor(MAC_prefix[:-1] , MAC_DB)

def get_netaddr(target , subnet):
	splittarget = target.split(".")
	ip = splittarget[0] + "." + splittarget[1] + "." + splittarget[2] + "." + "0/"+subnet
	return ip

def print_connected_devices(net_ip:str , MACDB, interface):
	print("clearing ARP cache...")
	os.system("ip neigh flush all")
	#print("arping start")
	#arping(net_ip)
	#print("arping end")

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

def list_available_ap(MACDB , interface):
	print("\n")
	networks = list(Cell.all(interface))
	print(networks)
	print("Wireless Networks :\n")
	print("{:16}	{:16}	{:16}	{:16}	{:16}".format("SSID","MAC","signal","quality","vendor"))
	for n in networks :
		if n.ssid != None :
			print("{:16}	{:16}	{:16}	{:16}	{:16}".format( n.ssid , n.address , n.signal , n.quality , MAC_to_vendor(n.address.upper() , MACDB )  ))

	print("\n")
	return networks


def open_menu(options:list , title="Menu" ):
	print(title)

	i = 0
	while i<=len(options)-1:
		print(i , "	" , options[i]) 
		i+=1

	choice = -1
	while choice not in range(0,len(options)):
		u_input = input("Select option (0-"+str(len(options) -1)+") : \n")
		if u_input.isdigit() :
			choice = int(u_input)
		if choice not in range(0,len(options)):
			print("\nIncorrect option given. Try again.\n")
	return choice

def log_this(collection , subdir = "") :
	name = input("\n Saisissez un nom/lieu :\n")

	if not os.path.isdir("./logs") :
		os.mkdir("./logs")
	if not os.path.isdir("./logs/"+subdir) :
		os.mkdir("./logs/"+subdir)


	filepath = "./logs/"+subdir+name+"-"+time.strftime("%Y-%m-%d_%H-%M-%S" , time.localtime())+".json" 
	with open( filepath , "w+" ) as f:
		json.dump(collection, f)
	print("Log saved at location :\n"+filepath+"\n")

def main():
	MainTitle = " __    __     _               _    \n/ / /\\ \\ \\___| |__   ___  ___| | __\n\\ \\/  \\/ / __| '_ \\ / _ \\/ __| |/ /\n \\  /\\  / (__| | | |  __/ (__|   < \n  \\/  \\/ \\___|_| |_|\\___|\\___|_|\\_\\\n                           By Pajul"
	print(MainTitle)
	MACDB = init_MAC_DB()

	available_interfaces = [ i for i in list(IFACES) if "wl" in i ]
	interface = available_interfaces[ open_menu(available_interfaces , "Select wireless interface") ]

	Evil_Twin_up = False
	running = True
	main_menu = ["EXIT" , "Create Evil Twin" , "Close Evil Twin" , "See Evil Twin's connections" , "List available Wi-Fi"]
	while running :
		result = open_menu(main_menu,"Main Menu")
		if result <= len(main_menu) :
			match result :
				case 0 :
					stop_hotspot()
					running = False
				case 1 :
					if  Evil_Twin_up :
						print("Evil Twin is already up.")
					else : 
						SSID = input("Enter SSID :\n")
						start_hotspot(SSID , interface = interface)
						Evil_Twin_up = True
				case 2 :
					if not Evil_Twin_up :
						print("Evil Twin is already down.") 
					else :
						stop_hotspot()
						Evil_Twin_up = False
				case 3 :
					if not Evil_Twin_up :
						print("\nEvil Twin is currently down, or the script has been interrupted unexpectedly. Choose EXIT (0) to reset connections.\n")
					else :
						print("\nscanning devices on : " ,  get_netaddr( get_if_addr(interface) , "24"))
						clients = print_connected_devices(get_netaddr(get_if_addr(interface) , "24"), MACDB , interface )

						user_choice = input("\nAre we logging this ? (y/N)\n")
						if user_choice == "y" or user_choice == "Y" :
							log_this(clients,subdir="con_dev/")
						print("\n")

				case 4 :

					networks = list_available_ap(MACDB , interface)
					user_choice = input("\nAre we logging this ? (y/N)\n")
					if user_choice == "y" or user_choice == "Y" :
						log_this( [ {"ssid":n.ssid, "address":n.address , "signal":n.signal , "quality" : n.quality , "vendor" : MAC_to_vendor(n.address.upper() , MACDB ) } for n in networks], subdir="av_APs/" )
if __name__ == "__main__" :
	main()
