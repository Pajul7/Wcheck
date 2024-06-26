import json
import csv
import os
import time

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


def log_this_csv(collection, subdir=""):
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
	print("{:16}	{:16}	{:10}	{:10}	{:16}	{:10}	{:10}	{:10}".format("SSID","MAC","signal","quality","frequency","encryption","channel","vendor"))
	for n in ap_list :

		if n["ssid"] != None :

			print("{:16}	{:16}	{:10}	{:10}	{:16}	{:10}	{:10}	{:10}".format( n["ssid"] , n["address"] , n["signal"] , n["quality"], n["frequency"], n["encryption"] , n["channel"] , n["vendor"]))
	
	print("\n")
