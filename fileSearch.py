"""FileSearch Module
Contains the functions needed to search SSIDs and MAC addresses in scan map dictionnaries.
"""

import csv
import json


def search_by_MAC( MAC:str , scan_map:dict ) :
    '''
    Takes a MAC address and a scan map dict, search the address and displays the results.
    '''
    for scan in scan_map :
        if MAC in scan_map[scan] :
            print('Found : '+ MAC +' in '+ scan +' :')
            print('\t', scan_map[scan][MAC]['ssid'] , scan_map[scan][MAC]['quality'] , scan_map[scan][MAC]['encryption'])

def search_by_SSID( SSID , scan_map ) :
    '''
    Takes a SSID and a scan map dict, search the SSID and displays the results.
    '''
    results = {}
    for scan in scan_map :
        for MAC in scan_map[scan] :

            if scan_map[scan][MAC]['ssid'] == SSID :

                if scan not in results:
                    results[scan] = []

                results[scan].append(scan_map[scan][MAC])

    for scan in results : 
        print("found", len(results[scan]) , "occurences of "+ SSID +" in "+ scan +" :")
        for ap in results[scan] : 
            print('\t'+ ap['address'] , ap['quality'] , ap['encryption'])
