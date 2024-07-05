import csv
import os 
import time

from Misc import *

def get_legitimate( path ) :
    '''
    Imports a file with access points to compare with scans.
    File must be a csv file with at least a "MAC" and "SSID" columns
    '''
    legitimate = {}

    with open(path , 'r') as f :
        reader = csv.DictReader(f , delimiter = ',' )
        for row in reader : 
            legitimate[row["MAC"]] = row["SSID"]
    return legitimate


def ap_delta( scans:list , legitimate:list ) :
    '''
    Takes a list of scans and a list of legitimate access points
    and return the difference : 
    MAC addresses in scans that are not in reference files
    Aps with good MAC addresses but wrong SSIDs.
    '''
    delta = []
    looked_addresses = []

    for ap in scans :
        print(ap)
        if ap[0]["address"] not in looked_addresses:
            if ap[0]["address"] not in legitimate :
                delta.append(ap[0])
            
            elif ap["ssid"] != legitimate[ ap[0]["address"] ]:
                delta.append(ap[0])
            
            looked_addresses.append(ap[0]["address"])

    return(delta)

def save_results( collection:list , name = "") :
    '''
    Exports an AP collection, result of a comparison in a single csv file under ./results.
    Takes an AP list and a file name.
    '''
    if name == "" :
        name = input("\n Saisissez un nom/lieu :\n")

    if not os.path.isdir("./results") :
        os.mkdir("./results")
    
    filepath = "./results/"+name+"-"+time.strftime("%Y-%m-%d_%H-%M-%S" , time.localtime())+".csv" 
    with open( filepath , "w+" ) as f:
        writer = csv.DictWriter( f , collection[0].keys() )

        writer.writeheader()
        for item in collection:    
            writer.writerow(item)

    print("Results saved at location :\n"+filepath+"\n")


def save_merged( collection , name=''):
    '''
    Takes an AP list and a name,
    and save all APs in a single file, adding the "scan" column,
    which contains the file they are from.
    '''
    if name == '' :
        name = input("\n Saisissez un nom/lieu :\n")

    if not os.path.isdir("./merged") :
        os.mkdir("./merged")
    
    filepath = "./merged/"+name+"-"+time.strftime("%Y-%m-%d_%H-%M-%S" , time.localtime())+".csv" 
    with open( filepath , "w+" ) as f:

        keys = ["ssid" , "address" , "signal" , "quality" , "frequency" , "encryption" , "channel" , "vendor" , "scan"]
        writer = csv.writer( f )

        writer.writerow(keys)

        for item , scan in collection:    

            item["scan"] = scan

            writer.writerow([ item[k] for k in keys ])
    print("Merged scans saved at location :\n"+filepath+"\n")
