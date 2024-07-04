import argparse
from Misc import *
from LegitimateComparison import *
import os.path


parser = argparse.ArgumentParser(description='Scans wireless access points.')
parser.add_argument('-S', help='Scan access point devices.', action='store_true')
parser.add_argument('-s', help='Save results in a csv file. Argument is a name, file name will be in format : <name>-<date>-<hour>.csv.', action='append')
parser.add_argument('-m', help='Merge results in a unique csv file. Needs a name to be specified.')
parser.add_argument('-c', help='Compare all scans currently in the logs directory with the given reference. Need reference file path as parameter.')
parser.add_argument('-d', help='Delete all scan logs.', action='store_true')
parser.add_argument('-i', help='Specify the interface used. /!\\ must be a wireless interface.', action='append')
parser.add_argument('-y', help='Skips confirmations.' , action='store_true')

parser.add_argument('--et-aup', help='Enable access point with selected detected SSID.' , action='store_true')
parser.add_argument('--et-mup', help='Enable an access point with given SSID.',action="store")
parser.add_argument('--et-scan', help='List all devices connected to our access point.' , action='store_true')
parser.add_argument('--et-down', help='Disable the access point.' , action='store_true')

arg_counts = {'s' : 0, 'i' : 0}

args , unknown = parser.parse_known_args()

arg_dict = vars(args)

if all( arg_dict[arg] == False or arg_dict[arg] == None for arg in arg_dict if arg not in ['s','i','y']) :
    print('Error : no valid arguments given. Try with -h for help.') 
    exit()


def next_arg_instance( arg_list , arg_name ) :
    if arg_list == None or arg_counts[arg_name] > len(arg_list) - 1 :
        return None
        
    else :
        res =  arg_list[arg_counts[arg_name]]

        arg_counts[arg_name] +=1 

        return res

def get_interface() :

    interface = next_arg_instance(args.i , 'i' )

    if not interface or not is_wireless(interface)  :
        print("Error : Interface given is empty, invalid or not a wireless interface. Please specify a valid one with -i.")
        exit()
    else :
        return interface

def get_save_name():
    return next_arg_instance(args.s , 's')

def main():

    MACDB = init_MAC_DB()

    valid_interface = False

    '''
    if args.i and is_wireless(args.i) :
        valid_interface = True
    '''

    print(args.i)

    if args.S == True :

        interface = get_interface()
        networks = list_available_ap(MACDB , interface)
        

        save_name = get_save_name()

        if save_name :
            log_this_csv( networks , subdir="scans/" , name = save_name )

    if args.m :
        save_merged(gather_scans() , args.m)

    if args.d :
        sure = args.y

        if not os.path.exists('./logs/scans/'):
            print("-d : No logs to delete.")
        else : 
                
            if not sure :
                if ( input("Are you sure you want to delete ALL of the scans ? (y/N)").upper() 
                in ["Y","YES"]) :
                    sure = True

            if sure :
                shutil.rmtree("./logs/scans/")
                print("Logs sucessfully deleted.")
            else :
                print("Deletion aborted.")
    
    if args.c :

        if not os.path.isfile(args.c):
            print("-c : No valid reference file given.")
        else :

            leg = get_legitimate(leg_name)
            d = gather_scans()
            r = ap_delta( d , leg )

            display_aps( r )


            save_name = get_save_name()

            if save_name : 
                save_results( r , save_name ) 


    if args.et_down :
        stop_hotspot()

    if args.et_aup :

        interface = get_interface()

        print("Select an access point to mimic SSID.")
        target_list = list_available_ap( MACDB , interface )

        target_i = input( "Target : ")

        if target_i.isdigit() and int(target_i) <= len(target_list) and int(target_i) > 0:
            stop_hotspot()
            start_hotspot(target_list[ int(target_i) - 1 ]["ssid"] , interface = interface)
        else : 
            print("Incorrect target number.")
            exit()

    elif args.et_mup :

        interface = get_interface()

        stop_hotspot()
        start_hotspot(args.et_mup , interface=interface)

    if args.et_scan :

        print("\nscanning devices on : " ,  get_netaddr( get_if_addr(interface) , "24"))

        clients = print_connected_devices(get_netaddr(get_if_addr(interface) , "24"), MACDB , interface )


        save_name = get_save_name()
        if save_name :
            log_this_csv(clients,subdir="et_clients/", name=save_name )


if __name__ == "__main__" :
    main()