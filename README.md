# sonion
Security Onion Packet Download scripts

Sonion is a suite of scripts used to pull pcaps based on date and time (or a date and time range) and a filter from a Security Onion sensor.  This way if you want to pull pcaps that are beyond the scope of an alert in Squert or a session in Elsa, you can cast a wider net.

The suite is made up of 3 scripts.  The most bulk of the work is done in sonion.py.  It should just work without modification (it pulls local hostname using uname, so hostname needs to match the sensor directory specifed in "/nsm/sensor_data/hostname-eth1/dailylogs/").  This script defaults to eth1 for the monitoring port. If your sensor uses a different sensor port you would need to edit the sodir variable definition line.

If the hostname and ethernet port are correct, create /opt/sonion/ directory and drop sonion.py in it. When creating the directory it only needs to allow execution and read. sonion.py also relies on tcpdump which should already be installed on any Security Onion sensor. The only other file required in the /opt/sonion/ directory is empty.pcap which is basically an empty pcap file used as a stub for the pcap file that will be built by sonion.py.

# sonion.py

NOTE - the following information on sonion.py is only useful if you are not using the sonion.sh client.  sonion.sh will ssh to the sensor and launch sonion.py, passing all of the required arguments.  Since sonion.sh is over an ssh session if you are parsing through a lot of data you may want to run sonion.py locally on the sensor and then the following information is valuable.

To run sonion.py:

/opt/sonion/sonion.py $date $time $filter $date2 $time2

$date = the date of the event or the start of the date range
$time = the time of the event (UTC) or the start time of the range
$date2 = the end of the date range - optional if not specifying a range
$time2 = the end of the time range (UTC) - optional if not specifying a range

Date and time format - YYYY-MM-DD HH:MM:SS  < the script is dumb and requires exactly this format.  Use zeroes to pad single digit values (example 2017-08-01 01:01:00)..  No values can be skipped.

$filter = the filter that specifies the IP's and ports you are looking for.  

There are two filter formats:

FILTER="$SRC+$DST-$SPRT+$DPRT"

example - 172.16.1.1+10.1.1.1-1025+80

$SRC and $DST are IP addresses for the socket pair
$SPRT and $DPRT are the ports for the socket pair
NOTE - although they are labeled "source and destination" these terms are arbitrary and the values will be used to build a basic bpf with logical and, so directionality actually doesn't matter

or

FILTER="BPF-net-172.16.1.10/24"

Any custome BPF filter can be added, but all spaces need to be replaced with -'s and it must be prefaced by BPF so sonion.py knows to treat it differently then the previous notation.  There is no error checking of BPF syntax, so if the syntax is wrong the tcpdump command will error out on the sensor.

Upon launch sonion.py should convert the specified date and time values to epoch values and use them to build a list (array) of dailylogs directorys and files.  Then using the specified filter, sonion.py uses tcpdump to find interesting packets in those files, create pcaps and merge them all together into one file in the /tmp directory named hostname_epoch.pcap, where hostname is the hostname as discovered by uname and epoch is the epoch translation of $date and $time. 

# sonion.sh

sonion.sh is client for the sonion.py script.  It is meant to be run from a local system which will then connect to the Security Onion sensor via ssh to pull full packet information.  It is a bash wrapper containing an expect script that is written to run on Mac OSX.  It should be easily converted to Linux with changes to the date conversion command.  

The syntax is: ./sonion.sh <3 letter site code>

Before using you will need to add your sensors' DNS resolvable hostnames to the predefined example sections:

elif [ "$1" == "xxx" ]
then
    so="xxx.sensor.domain"
    echo -e "Sensor set to xxx"
    
where xxx is an arbitrary 3 digit code and xxx.sensor.domain is the resolvable sensor name (NOTE - the resolvable hostname used here must also match the hostname of the sensor as retreived with uname, as well as the hostname used in the "/nsm/sensor_data/hostname-eth1/dailylogs/" directory for everything to work correctly).

Upon running it will prompt for the following information:

Enter Date in UTC [YYYY-MM-DD HH:MM:SS]: 2017-09-02 12:00:00
Enter End Time and Date in UTC or press Enter  [YYYY-MM-DD HH:MM:SS]:
Enter Source IP: 172.16.100.1
Enter Source Port: 445
Enter Destination IP:
Enter Destination Port:

One date can be entered and the 5 sensor files closest to the time specified (before and after - assuming that many files exist on that date) will be filtered for the IP and port information specified.  At least one IP address should be specified, but adding as much information as possible is recommended in heavy traffic environments.  As noted previously since these items are used to construct a basic BPF, Source and Destination is arbitrary and doesn't matter.  There is no real directionality considered.

To use a custom BPF enter a second command line argument of x.  

./sonion.sh sensorcode x

Instead of being prompted for IP's and ports you will be asked to enter your custom BPF (no error checking is done so it will error out if it isn't entered correctly).  

After this information is entered Expect will spawn an ssh session to the sensor with Xwindows support.  So an x-server needs to be running on the client system (tested with Xquartz).  You will be prompted to enter your local sensor authentication credentials (if you don't have any they will need to be created).  Note - the current spawn command doesn't specify a username, so it uses the current user login name. For simplicity if you create a matching user name on your Security Onion sensors, no authentication alternations will be required in the sonion.sh script.  You will be prompted for your password and the session will be established, sonion.py will be run with the information specified above (it will be passed as explained in the sonion.py section).  Sonion.sh will also create a file (/tmp/pcap.file) on your local client system with the name that will be used for the pcap file to be generated on the sensor.  This is for use with soxfer.exp.  After the pcap is generated by sonion.py, sonion.sh will open it with wireshark over Xwindows. This way a large pcap files doesn't need to be downloaded to your local system.  If your ssh session times out or you want the file transferred to your local system use soxfer.exp. 

# soxfer.exp 

soxfer.exp is an expect script used to download a pcap generated by sonion.py from a Security Onion sensor to your local client system.  If you run it with no argument it will look locally in /tmp/pcap.file to find the name of the last pcap generated and download it accordingly. If you specify a filename as an argument it will attempt to download it instead.  After downloading the pcap soxfer.exp will automatically attempt to open the pcap with wireshark, so wireshark must be installed locally and in path for auto-open to function properly.


