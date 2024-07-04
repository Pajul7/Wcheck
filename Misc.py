import json
import csv
import os
import time
from pyroute2 import IPRoute, IW

def is_wireless(interface):
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
    res = {}
    with open("fMAC_DB.json") as f :
        res = json.load(f)
    return res

def MAC_to_vendor(MAC_prefix:str , MAC_DB:dict) :
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

def open_menu(options:list , title="Menu" ):
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

def list_available_ap(MACDB , interface):
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

def log_this_json(collection , subdir = "") :
    name = input("\n Saisissez un nom/lieu :\n")
    if not os.path.isdir("./logs") :
        os.mkdir("./logs")
    if not os.path.isdir("./logs/"+subdir) :
        os.mkdir("./logs/"+subdir)
    filepath = "./logs/"+subdir+name+"-"+time.strftime("%Y-%m-%d_%H-%M-%S" , time.localtime())+".json" 
    with open( filepath , "w+" ) as f:
        json.dump(collection, f)
    print("Log saved at location :\n"+filepath+"\n")


def log_this_csv(collection, subdir="", name=''):

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


def display_aps(ap_list) :

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
