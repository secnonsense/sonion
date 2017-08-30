#Check for argument, if not there print usage message
if [ -z "$1" ]
  then
    echo -e "\n"
    echo -e "Syntax is: ./sonion.sh <3 letter site code>"
    echo -e "Options are currently: col, bal or cos"
    echo -e "\n"
    exit
#check for 3 letter site code and assign so variable to correct IP    
elif [ "$1" == "col" ]
then
    so="172.20.100.65"
    echo -e "Sensor set to col-sos-001"
elif [ "$1" == "cos" ]
then
    so="172.20.100.83"
    echo -e "Sensor set to col-so-001"
elif [ "$1" == "bal" ]
then
    so="172.25.102.27"
    echo -e "Sensor set to bal-sos-001"
elif [ "$1" == "tst" ]
then
    so="thermaltake"
    echo -e "Sensor set to tst sensor"
#Fail out with error if any other 3 letter code entered
else
  echo -e "\n"
  echo -e "Invalid sensor 3 letter code.  Should be col, bal or cos"
  exit
fi
#Prompt for Date/Time and IP and port information
echo -e "\n"
while [[ ! $DATE =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; do
  read -p "Enter Date in UTC [YYYY-MM-DD HH:MM:SS]: " DATE  
done
while [[ ! $DATE2 =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; do
read -p "Enter End Time and Date in UTC or press Enter  [YYYY-MM-DD HH:MM:SS]: " DATE2
if [[ "$DATE2" == "" ]]; then
   break
fi    
done
#Check for x as second argument to enter freeform BPF
if [ "$2" == "x" ]
  then
  read -p "Enter Custom BPF: " FILTER_IN
  FILTER="BPF-$(echo $FILTER_IN | tr " " "-")"
  echo -e "\n"
#Input IP's and Ports.  Use basic regex input validation
else
  while [[ ! $SRC =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; do
  read -p "Enter Source IP: " SRC
  if [[ "$SRC" == "" ]]; then
     break
  fi    
  done
  while [[ ! $SPRT =~ ^[0-9]{1,5}$ ]]; do
  read -p "Enter Source Port: " SPRT
  if [[ "$SPRT" == "" ]]; then
     break
  fi    
  done
  while [[ ! $DST =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; do
  read -p "Enter Destination IP: " DST
  if [[ "$DST" == "" ]]; then
     break
  fi    
  done
  while [[ ! $DPRT =~ ^[0-9]{1,5}$ ]]; do
  read -p "Enter Destination Port: " DPRT
  if [[ "$DPRT" == "" ]]; then
     break
  fi    
  done
  echo -e "\n"
#Create FILTER variable with delimeters for easy parsing
  FILTER="$SRC+$DST-$SPRT+$DPRT"
fi
#Turn the Date/Time value into an array
array=($DATE)
array2=($DATE2)

#Convert Date and Time into Epoch format  
epoch="$(date -u -j -f "%Y-%m-%d %H:%M:%S" "$DATE" +%s)"
#create file in tmp containing capture file name
echo -e $so"_"$epoch".pcap" > /tmp/pcap.file

date=${array[0]}
time=${array[1]}
date2=${array2[0]}
time2=${array2[1]}

read -s -p "Enter Onion Password: " pass

# Set variables based on passed arguments

so=$so  
date=$date
time=$time
date2=$date2
time2=$time2
epoch=$epoch
filter=$FILTER
pass=$pass

expect << END

spawn ssh -X $so

# Lower timeout while password is being passed to server
set timeout 7

# Check to see if it is a known_host or send password
expect {
      "no)?" { send "yes\r"; exp_continue}
      "assword:" { send "$pass\r" }
}

# Check to see if password was accepted or error out
expect {
     "assword:" { send_user "\n"; send_user -- "Bad Password.. exiting \n"; exit}
     "$" { exp_continue}
}

# Raise timeout to give appropriate time to process commands
set timeout 1200

# open sonion.py script on SO server with date time and filter arguments
send "/opt/sonion/sonion.py $date $time $filter $date2 $time2\r";

# Wait for prompt to return after remote script has been processed
expect "Pcap File Generated!"

send "wireshark -r /tmp/${so}_${epoch}.pcap\r";

send_user "Capture loading..";

expect "$"

send_user "Completed";

sleep 2

send \003;

send "exit\r";

END
