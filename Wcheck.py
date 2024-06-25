import os
import shutil
from wifi import Cell, Scheme

from Misc import *
from Eviltwin import *
from LegitimateComparison import *

# Uncomment this to run it from outside of the script's directory.
os.chdir("/home/pajul/Documents/work/Wcheck/")


def list_available_ap(MACDB , interface):
	print("\n")
	networks = [{"ssid":n.ssid,"address":n.address,"signal":n.signal,"quality":n.quality, "frequency":n.frequency ,"channel":n.channel, "vendor":MAC_to_vendor(n.address.upper() , MACDB )} for n in list(Cell.all(interface))]

	print(networks)

	display_aps(networks)

	return networks

def main():
	MainTitle = " __    __     _               _    \n/ / /\\ \\ \\___| |__   ___  ___| | __\n\\ \\/  \\/ / __| '_ \\ / _ \\/ __| |/ /\n \\  /\\  / (__| | | |  __/ (__|   < \n  \\/  \\/ \\___|_| |_|\\___|\\___|_|\\_\\\n                           By Pajul"
	print(MainTitle)
	MACDB = init_MAC_DB()

	available_interfaces = [ i for i in list(IFACES) if "wl" in i ]
	interface = available_interfaces[ open_menu(available_interfaces , "Select wireless interface") ]

	Evil_Twin_up = False
	running = True
	main_menu = ["EXIT" , "Create Evil Twin" , "Close Evil Twin" , "See Evil Twin's connections" , "List available Wi-Fi", "Process data", "Delete logs", "Delete results","Merge logs"]
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
							log_this_csv(clients,subdir="con_dev/")
						print("\n")

				case 4 :

					networks = list_available_ap(MACDB , interface)
					user_choice = input("\nAre we logging this ? (y/N)\n")
					if user_choice == "y" or user_choice == "Y" :
						log_this_csv( networks , subdir="av_APs/" )

				case 5 :

					leg_name = input("Enter known legitimate APs file path (if empty will check './legitimate.csv') :\n")
					if leg_name == "" : leg_name = "./legitimate.csv"

					if  not os.path.isfile(leg_name) :
						print("Error : specified file does not exist.")
						break

					leg = get_legitimate(leg_name)

					d = gather_scans()

					r = ap_delta( d , leg )

					display_aps( r )

					if input("\nAre we saving this ? (Y/n)\n").upper() in ["Y","YES",""] :
						save_results( r ) 
				
				case 6 :
					if os.path.isdir("./logs"):
						sure = input("Are you sure you want to delete ALL of the scans ? (Y/n)")

						if sure.upper() in ["Y","YES",""] :
							shutil.rmtree("./logs")
							print("Logs sucessfully deleted.")
						else :
							print("Deletion cancelled.")
					else :
						print("There is currently no logs to delete.")

				case 7 :
					
					if os.path.isdir("./results"):	
						sure = input("Are you sure you want to delete ALL of the results ? (y/N)")

						if sure.upper() in ["Y","YES"] :
							shutil.rmtree("./results")
							print("Results sucessfully deleted.")
						else :
							print("Deletion cancelled.")
					else :
						print("There is currently no results to delete.")
				case 8 :

					if os.path.isdir("./logs/av_APs/") :
						
						save_merged(gather_scans())

					else :
						print("No scans to merge.")
if __name__ == "__main__" :
	main()
