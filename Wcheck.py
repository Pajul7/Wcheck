import argparse
from Misc import *
from fileSearch import *
from Eviltwin  import *
from LegitimateComparison import *
import os.path
import shutil

class OrderElementsAction(argparse.Action):
    def __call__(self, parser, namespace, values=None, option_string=None):
        if not 'ordered_args' in namespace:
            setattr(namespace, 'ordered_args', [])
        previous = namespace.ordered_args
        previous.append((self.dest, values))
        setattr(namespace, 'ordered_args', previous)



parser = argparse.ArgumentParser(description='Scans wireless access points.')
parser.add_argument('-S','--scan', help='Scan access point devices. -s possible', metavar='<ifname>', action=OrderElementsAction)
parser.add_argument('-s','--save', help='Save results in a csv file. Argument is a name, file name will be in format : <save_name>-<date>-<hour>.csv.', action='append', metavar='<save_name>')
parser.add_argument('-p','--process', help='Processes every scan file in a "scan map", in which you can search through.',action=OrderElementsAction,metavar='<map_name>')
parser.add_argument('-m','--merge', help='Merge results in a unique csv file. Needs a name to be specified.', metavar='<merge_name>', action=OrderElementsAction)
parser.add_argument('-c','--compare', help='Compare all scans currently in the logs directory with the given reference. Need reference file path as parameter. -s possible.', metavar='<comparison_name>', action=OrderElementsAction)
parser.add_argument('-wm','--where-mac', help='Look for a MAC address in the specified map', action=OrderElementsAction , nargs=2, metavar=('<MAC>','<scan_map_path>'))
parser.add_argument('-ws','--where-ssid', help='Look for a SSID in the specified map', action=OrderElementsAction , nargs=2, metavar=('<SSID>','<scan_map_path>'))
parser.add_argument('-d','--delete-logs', help='Delete all scan logs.', action=OrderElementsAction , nargs=0)
parser.add_argument('-y','--yes', help='Skips confirmations.' , action='store_true')

parser.add_argument('-et-aup','--evilTwin-auto-up', help='Enable access point with selected detected SSID.', metavar='<ifname>', action=OrderElementsAction)
parser.add_argument('-et-mup','--evilTwin-manual-up', help='Enable an access point with given SSID.', nargs=2 , metavar= ('<ifname>','<SSID>'), action=OrderElementsAction)
parser.add_argument('-et-scan','--evilTwin-scan', help='List all devices connected to our access point. -s possible.' , metavar='<ifname>', action=OrderElementsAction)
parser.add_argument('-et-down','--evilTwin-down', help='Disable the access point and deletes the connection.' , action=OrderElementsAction , nargs=0)

arg_counts = {'s' : 0}

args , unknown = parser.parse_known_args()

arg_dict = vars(args)

if all( arg_dict[arg] == False or arg_dict[arg] == None for arg in arg_dict if arg not in ['s','i','y']) :
    print('Error : no valid arguments given. Try with -h for help.') 
    exit()


def next_arg_instance( arg_list , arg_name ) :
    '''
    Search for the next content of the given argument name, and returns it if there is one.
    if none , returns None.
    '''
    if arg_list == None or arg_counts[arg_name] > len(arg_list) - 1 :
        return None
        
    else :
        res =  arg_list[arg_counts[arg_name]]

        arg_counts[arg_name] +=1 

        return res

def get_save_name():
    '''
    Get next specified save name in the given call arguments
    '''
    return next_arg_instance(args.save , 's')

def delete_logs() :
    '''
    Deletes ./logs/scans Directory.
    '''
    sure = args.yes

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

def scan(ifname , macdb) :
    '''
    Shortcut for performing a scan and saving it if specified.
    '''
    networks = list_available_ap(macdb , ifname)
    

    save_name = get_save_name()

    if save_name :
        log_this_csv( networks , subdir="scans/" , name = save_name )

def merge(merge_name) :
    '''
    Shortcut for performing a merge.
    '''
    save_merged(gather_scans() , merge_name)
    
def compare(reference_file_path):
    if not os.path.isfile(reference_file_path):
        print("-c : No valid reference file given.")
    else :

        leg = get_legitimate(reference_file_path)
        d = gather_scans()
        r = ap_delta( d , leg )

        display_aps( r )


        save_name = get_save_name()

        if save_name : 
            save_results( r , save_name ) 

def evilTwin_down() :
    '''
    Shortcut for stopping hotspot
    '''
    stop_hotspot()

def evilTwin_auto_up(MACDB , interface) :
    '''
    Shortcut for turning on the hotspot with a mimic selection.
    '''

    print("Select an access point to mimic SSID.")
    target_list = list_available_ap( MACDB , interface )

    target_i = input( "Target : ")

    if target_i.isdigit() and int(target_i) <= len(target_list) and int(target_i) > 0:
        stop_hotspot()
        start_hotspot(target_list[ int(target_i) - 1 ]["ssid"] , interface = interface)
    else : 
        print("Incorrect target number.")
        exit()

def evilTwin_manual_up(ifname , ssid ) :
    '''
    Shortcut for turning on the hotspot with specified SSID.
    '''
    stop_hotspot()
    start_hotspot( ssid , interface=ifname)

def evilTwin_scan(ifname , MAC_DB) :

    print("\nscanning devices on : " ,  get_netaddr( get_if_addr(ifname) , "24"))

    clients = print_connected_devices(get_netaddr(get_if_addr(ifname) , "24"), MAC_DB , ifname )


    save_name = get_save_name()
    if save_name :
        log_this_csv(clients,subdir="et_clients/", name=save_name )

def where_mac(MAC:str , path:str):
    '''
    Shortcut for searching a MAC address in the specified scan map filepath
    '''
    data={}

    with open(path, 'r') as f :
        data = json.load(f)

    search_by_MAC(MAC , data)

def where_ssid(SSID:str , path:str):
    '''
    Shortcut for searching an SSID in the specified scan map filepath
    '''

    data={}

    with open(path, 'r') as f :
        data = json.load(f)

    search_by_SSID(SSID , data)

def process(name:str) :
    '''
    Shortcut to process scans.
    '''
    process_scans(name)

def main():

    os.chdir(os.path.dirname(__file__))

    MACDB = init_MAC_DB()

    for arg in args.ordered_args :

        match arg[0]:

            case 'scan':
                scan( ifname = arg[1] , macdb = MACDB)

            case 'merge' :
                merge( merge_name = arg[1] )

            case 'process' : 
                process( name = arg[1] )

            case 'compare' : 
                compare( reference_file_path = arg[1] )
            
            case 'where_mac' :
                where_mac( MAC=arg[1][0] , path=arg[1][1] )

            case 'where_ssid' :
                print(arg)
                where_ssid( SSID=arg[1][0] , path=arg[1][1] )

            case 'delete_logs' :
                delete_logs()
            
            case 'evilTwin_down' :
                evilTwin_down()
            
            case 'evilTwin_auto_up':
                evilTwin_auto_up(MACDB, interface=arg[1])
            
            case 'evilTwin_manual_up':
                evilTwin_manual_up( ifname = arg[1][0] , ssid = arg[1][1] )
            
            case 'evilTwin_scan':
                evilTwin_scan( ifname = arg[1] , MAC_DB=MACDB)

if __name__ == "__main__" :
    main()