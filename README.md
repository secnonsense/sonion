# sonion
Security Onion Packet Download scripts

Sonion is a suite of scripts to pull pcaps based on date and time (or a date and time range) and a filter.  This way if you want to pull pcaps that are beyond the scope of an alert in Squert or a session in Elsa, you can cast a wider net.

The suite is made up of 3 scripts.  The most important is sonion.py.  It should just work without modification (it pulls local hostname using uname, so hostname needs to match the sensor directory specifed in "/nsm/sensor_data/hostname-eth1/dailylogs/".  This script defaults to eth1 for the monitoring port. If your sensor uses a different sensor port you would need to edit the sodir variable definition line.

If the hostname and ethernet port are correct, create /opt/sonion/ directory and drop sonion.py in it. When creating the directory it only needs to allow execution and read. sonion.py also relies on tcpdump which should already be installed on any Security Onion sensor.

to run:

/opt/sonion/sonion.py $date $time $filter $date2 $time2

$date = the date of the event or the start of the date range
$time = the time of the event (UTC) or the start time of the range
$date2 = the end of the date range - optional if not specifying a range
$time2 = the end of the time range (UTC) - optional if not specifying a range

Date and time format - YYYY-MM-DD HH:MM:SS  < the script is dumb and requires exactly this format.  Use zeroes to pad single digit values (example 2017-08-01 01:01:00)..  No values can be skipped.

$filter = the filter that specifies the IP's and ports you are looking for.  

There are two filter formats:

FILTER="$SRC+$DST-$SPRT+$DPRT"

$SRC and $DST are IP addresses for the socket pair
$SPRT and $DPRT are the ports for the socket pair
NOTE - although they are labeled "source and destination" these terms are arbitrary and the values will be used to build a basic bpf with logical and, so directionality actually doesn't matter

or

FILTER="BPF-net-172.16.1.10/24"

Any custome BPF filter can be added, but all spaces need to be replaced with -'s and it must be prefaced by BPF so sonion.py knows to treat it differently then the previous notation.

Upon launch sonion.py should convert the specified date and time values to epoch values and use them to build a list (array) of dailylogs directorys and files.  Then using the specified filter, sonion.py uses tcpdump to find interesting packets in those files, create pcaps and merge them all together into one file in the /tmp directory named hostname_epoch.pcap, where hostname is the hostname as discovered by uname and epoch is the epoch translation of $date and $time. 

