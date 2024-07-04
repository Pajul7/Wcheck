from scapy.all import srp , Ether , ARP , arping , IFACES , get_if_addr
from os import system
from Misc import *
import nmcli
import subprocess
from time import sleep

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
        print ("{:16}    {:16}    {}".format(  c["ip"], c["mac"] , MAC_to_vendor( c["mac"].upper() , MACDB)    ))
    return clients

def restart_network_manager():
    print("Restarting NetworkManager service...")
    subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"])
    print("Waiting 10s for it to wake up...")
    sleep(10)

def is_hotspot_on():
    try :
        nmcli.connection.show('WCHECK-CONNECTION')
    except nmcli.NotExistException :
        return False
    else : 
        return True


def start_hotspot(SSID:str , interface:str , con_name="WCHECK-CONNECTION", band="bg"):
    print("Starting hotspot...")

    if is_hotspot_on():
        print("Hotspot is already on. Restarting with given parameters...")
        stop_hotspot()
        sleep(3)    

    retried = False
    done = False

    while not done :
        results = subprocess.run(
            ["sudo" , "nmcli" , "con" , "add" , "type" , "wifi" , "con-name" , con_name, "autoconnect", "no", "wifi.mode", "ap", "wifi.ssid", SSID, "ipv4.method", "shared", "ipv6.method", "shared"],
            capture_output=True,
            text=True
        )

        print("DEBUG : ",results.stderr)
        if results.stderr != "" :
            if not retried :
                print("NetworkManager seems to fail. Restarting NetworkManager Service...")
                restart_network_manager()
                print("NetworkManager restarted.")
                retried = True
            else :
                print("It seems there is a problem with NetworkManager or your interface. Fix it and try again later.")
                print(results.stderr)
                exit()
        else :
            subprocess.run(["sudo", "nmcli", "con", "up", con_name])
            done = True


    sleep(3)
    print("Hotspot on.")

def stop_hotspot(con_name="WCHECK-CONNECTION"):
    print("Stopping hotspot...")

    try:
        print("Turning off Hotspot...")
        nmcli.connection.down(con_name)
    except:
        print("Connection already off.")

    if is_hotspot_on():
        print("Deleting connection...")
        nmcli.connection.delete(con_name)
        sleep(2)
        print("Connection deleted.")

    else :
        print("hotspot is already down.")
