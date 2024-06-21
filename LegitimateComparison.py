import csv
import os 
import time

def get_legitimate( path ) :
    legitimate = {}

    with open(path , 'r') as f :
        reader = csv.DictReader(f , delimiter = ',' )
        for row in reader : 
            legitimate[row["MAC"]] = row["SSID"]
    return legitimate

def gather_scans():
    log_data = []

    log_name_list = os.listdir("./logs/av_APs/")
    for log in log_name_list :

        print("Gathering "+log+" ...")

        with open("./logs/av_APs/"+log , 'r') as f :
            reader = csv.DictReader(f , delimiter = ',')
            for row in reader :
                log_data.append(row)

    return(log_data)

def ap_delta( scans , legitimate ) :
    delta = []
    looked_addresses = []

    for ap in scans :
        if ap["address"] not in looked_addresses:
            if ap["address"] not in legitimate :
                delta.append(ap)
            
            elif ap["ssid"] != legitimate[ ap["address"] ]:
                delta.append(ap)
            
            looked_addresses.append(ap["address"])

    return(delta)

def save_results( collection ) :
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


