""" Misc Module
Contains Various function that does not really fit elsewhere, or that are used in different places.
"""

import json
import csv
import os
import time
from pyroute2 import IPRoute, IW
from wifi import Cell, Scheme
import ipaddress

def is_wireless(interface:str):
    '''
    Takes a name and returns True if it is a valid wireless interface name.
    '''
    ipr = IPRoute()
    iw = IW()
    try:
        # Get index interface
        idx = ipr.link_lookup(ifname=interface)[0]
        # get wireless info 
        iw_info = iw.get_interface_by_ifindex(idx)
        if iw_info:
            return True
    except IndexError:
        return False
    return False

def init_MAC_DB():
    '''
    Imports the MAC address file and return a dictionnary, to search for vendors from MAC address later.
    '''
    res = {}
    with open("fMAC_DB.json") as f :
        res = json.load(f)
    return res

def MAC_to_vendor(MAC_prefix:str , MAC_DB:dict) :
    '''
    Takes a MAC address and a MAC/vendor dict.
    MAC addresses/prefixes must be keys and vendors, values.
    '''
    if len(MAC_prefix) < 8 :
        return "Unknown"

    elif MAC_prefix in MAC_DB :
        return MAC_DB[MAC_prefix]["vendorName"]
    else :
        if MAC_prefix[-2] == ':' :
            return MAC_to_vendor(MAC_prefix[:-2] , MAC_DB)
        else :
            return MAC_to_vendor(MAC_prefix[:-1] , MAC_DB)

def get_netaddr(target:str , subnet:str):
    '''
    Takes an host ip address and a subnet mask number (CIDR notation), and returns the network address
    '''
    cidr_notation = target+'/'+subnet
    network = ipaddress.ip_network(cidr_notation, strict=False)
    return str(network.network_address)

def open_menu(options:list , title="Menu" ):
    '''
    Takes a list of options and a title, display a menu with given choices.
    Returns the choosen option's index.
    '''
    print(title)

    i = 0
    while i<=len(options)-1:
        print(i , "    " , options[i]) 
        i+=1

    choice = -1
    while choice not in range(0,len(options)):
        u_input = input("Select option (0-"+str(len(options) -1)+") : \n")
        if u_input.isdigit() :
            choice = int(u_input)
        if choice not in range(0,len(options)):
            print("\nIncorrect option given. Try again.\n")
    return choice

def list_available_ap(MACDB:dict , interface:str):
    '''
    Takes the MAC/vendor dict and an interface, gather the access points
    detected by the interface, displays and returns them.
    /!\\ if your interface is already connected to an access point, you will only see this ap.
    '''
    print("\n")
    networks = [
        {
            "ssid":            n.ssid,
            "address":        n.address,
            "signal":        n.signal,
            "quality":        n.quality,
            "frequency":    n.frequency,
            "encryption":    n.encryption_type if n.encrypted else "-- NONE --" ,
            "channel":        n.channel,
            "vendor":        MAC_to_vendor(n.address.upper() , MACDB )
        } for n in list(Cell.all(interface))
    ]

    display_aps(networks)

    return networks

def gather_scans():
    '''
    Gather all scans in ./logs/scans and returns a list of tuple ( ap_dict , scan_name )
    '''

    log_data = []

    log_name_list = os.listdir("./logs/scans/")
    for log in log_name_list :

        print("Gathering "+log+" ...")

        with open("./logs/scans/"+log , 'r') as f :
            reader = csv.DictReader(f , delimiter = ',')

            for row in reader :
                log_data.append((row , log))
    return(log_data)

def log_this_csv(collection:list, subdir="", name=''):
    '''
    Takes a list of access points and stores it in a csv file.
    '''
    if name == '' :
        name = input("\n Saisissez un nom/lieu :\n")
    
    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    if not os.path.isdir("./logs/" + subdir):
        os.mkdir("./logs/" + subdir)

    filepath = "./logs/" + subdir + name + "-" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ".csv"
    with open(filepath, "w+") as f:
        writer = csv.DictWriter(f, fieldnames=collection[0].keys())

        writer.writeheader()
        for item in collection:
            writer.writerow(item)
        
        f.flush()  # Vider le buffer Python
        os.fsync(f.fileno())  # Vider le buffer du système d'exploitation

    print("Log saved at location :\n" + filepath + "\n")

def process_scans(name:str):
    '''
    Gets all the scan logs in /logs/scans and saves them in a json file which
    allows fast searches.
    '''
    
    result = {}

    if not os.path.isdir("./logs"):
        os.mkdir("./logs")
    if not os.path.isdir("./logs/maps"):
        os.mkdir("./logs/maps")

    scans = gather_scans()


    for scan in scans : 
        if scan[1] not in result :
            result[scan[1]] = {}

        result[scan[1]][scan[0]['address']] = scan[0]
    
    filepath = "./logs/maps/" + name + "-" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + ".json"

    with open(filepath , '+w') as f :
        json.dump(result , f)
    print("Scan Map saved at location : " + filepath)



def display_aps(ap_list:list) :
    '''
    Takes a list of access point dicts, and displays them nicely with
    SSID,MAC address,signal,quality,frequency,encryption,channel and vendor.
    '''
    print("Access points :\n")
    print("   {:16}    {:16}   {:10}   {:10}   {:16}   {:10}   {:10}   {:10}"
        .format(
            "SSID",
            "MAC",
            "signal",
            "quality",
            "frequency",
            "encryption",
            "channel",
            "vendor"
        )
    )
    i = 1
    for n in ap_list :

        if n["ssid"] != None :

            print("{}  {:16}    {:16}    {:10}    {:10}    {:16}    {:10}    {:10}    {:10}"
                .format( 
                    i,
                    str(n["ssid"]),
                    str(n["address"]),
                    str(n["signal"]),
                    str(n["quality"]),
                    str(n["frequency"]),
                    str(n["encryption"]),
                    str(n["channel"]),
                    str(n["vendor"])
                )
            )
        i+=1
    
    print("\n")
