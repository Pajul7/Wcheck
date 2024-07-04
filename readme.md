# Wcheck

## Dependencies

Wcheck runs on linux with python 3.
To run, it needs the following non-standard libraries : 
> wifi , scapy , pyroute2 , nmcli

And needs to have Network Manager (nmcli command) installed.

## Description :

Wcheck is a small utility made to list available wireless access points,
and to create access points in order to insure that hosts do not auto connect to
malicious access points with SSIDs they already know.

## Use :

Help message : 

'''
usage: Wcheck.py [-h] [-S <ifname>] [-s <save_name>] [-m <merge_name>] [-c <comparison_name>] [-d] [-y] [-et-aup <ifname>] [-et-mup <ifname> <SSID>] [-et-scan <ifname>] [-et-down]

Scans wireless access points.

options:
  -h, --help            show this help message and exit
  -S <ifname>, --scan <ifname>
                        Scan access point devices. -s possible
  -s <save_name>, --save <save_name>
                        Save results in a csv file. Argument is a name, file name will be in format : <save_name>-<date>-<hour>.csv.
  -m <merge_name>, --merge <merge_name>
                        Merge results in a unique csv file. Needs a name to be specified.
  -c <comparison_name>, --compare <comparison_name>
                        Compare all scans currently in the logs directory with the given reference. Need reference file path as parameter. -s possible.
  -d, --delete-logs     Delete all scan logs.
  -y, --yes             Skips confirmations.
  -et-aup <ifname>, --evilTwin-auto-up <ifname>
                        Enable access point with selected detected SSID.
  -et-mup <ifname> <SSID>, --evilTwin-manual-up <ifname> <SSID>
                        Enable an access point with given SSID.
  -et-scan <ifname>, --evilTwin-scan <ifname>
                        List all devices connected to our access point. -s possible.
  -et-down, --evilTwin-down
                        Disable the access point and deletes the connection.
'''

Note that you cannot have multiple hotspots at a time.

