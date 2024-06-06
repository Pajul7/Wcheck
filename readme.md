# Wcheck
## Author : Pajul

## Dependencies

Wcheck runs on linux with python 3.
To run, it needs the following libraries : 
>os , time , json , wifi , scapy

And needs to have Network Manager (nmcli command) installed.

## Description :

Wcheck is a small utility made to list avaliable wireless access points,
and to create access points in order to insure that hosts do not auto connect to
malicious access points with SSIDs they already know.

## Usage

Very simple.
Run Wcheck.py with python, choose a valid wireless interface,
and the main menu will appear.
Valid wireless interfaces are wlan.
The same interface will be used for all next actions.
You can choose between 5 options :


### 0 - EXIT 

EXIT will... well exit. Please note that it will also delete the access point connection.
If the program exits unexpectedly, connections will stay up.
To remove them, you can do it manually using : 

 >nmcli con delete WCHECK-CON

or simply run the script again and EXIT.

### 1 - Create Evil Twin

This one will create an access point with the specified SSID, on the specified interface.
Will refuse if an access point has already been created since the start of wcheck.py.

### 2 - Close Evil Twin

Will close the access point if one has already been created since the start of wcheck.py.
That's all ?
Yes.

### 3 - See Evil's Twin connections

Lists the devices connected to the access point, using ARP.
Showing MAC address and adapter vendor.
You can log the results in a json file, in the logs directory, included with the script.

### 4 - List available Wi-Fi

This one is pretty self-explanatory.
Will print out SSID, MAC address, signal, quality.
You can log the results in a json file, in the logs directory, included with the script.


/!\ This is a small newbie script, dont judge it too harshly.
