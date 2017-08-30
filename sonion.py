#!/usr/bin/python

import os,sys,time
from subprocess import call

host = os.uname()[1]

print "my host is: " , host

date = sys.argv[1] + " " + sys.argv[2]

epoch = str(int(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S'))))

print "epoch date is: " , epoch

if len(sys.argv) > 4: 
   date2 = sys.argv[4] + " " + sys.argv[5]
   epoch2=str(int(time.mktime(time.strptime(date2, '%Y-%m-%d %H:%M:%S'))))
   print "epoch2 date is: " , epoch2    
else:
   epoch2 = ""
   date2 = "" 

# Manually assinged the correct packet capture directory for this SO server
sodir = host + "-eth1"

print "sodir is: " , sodir              
                            
index = start = end = counter = 0 
answer = answer2 = ""
x, d, e, m, array, FILTERS, FLITERIP, FILTERPRT = ([] for i in range(8))
a = 3
z = 1

# set packet capture directory
dird = "/nsm/sensor_data/" + sodir + "/dailylogs/"

# if we have an epoch2 find and make an array of all  date directories encompassing epoch and epoch2
if epoch2 != "":
   for filename in os.listdir(dird):
         d.append(filename)

   d.sort()

   for w in d:
         if w == sys.argv[1]:
             start = 1
         if start == 1 and end == 0:
             m.append(w)
         if w == date2:
             break
# otherwise with just a single epoch make an array with a single value -  the date provided
else:
   m.append(sys.argv[1])

for cdir in m:
   dirx = dird + cdir
   counter = counter + 1
   if answer != "" and answer2 != "":
         break

# read in files from directory, spilt them apart and assign the portion named by the epoch to an array x
   for filename in os.listdir(dirx):
         ep = filename.split('.')
         index = index +1
         x.append(ep[2])

# make sure the array is in order 
   x.sort()

# find the answer by comparing epochs in the array to the epoch of entered by client
   for y in range (0,index):
         if x[y] > epoch and answer == "":
              answer = x[y-1]
              q = y
              array.append(answer)

# step backwards 2 files to expand the data pool but only if there was no epoch2 specified
              if epoch2 == "":
                 for j in range (y-1,y-a,-1):
                    if j == 0:
		       break
                    array.append(x[j-1])
# step forwards 2 files to expand the data pool
                 for k in range (y-1,y+z,1):
                    if k+1 == index:
                       break
                    array.append(x[k+1])
# confirm epoch2 has a value and find the value
         if x[y] > epoch2 and epoch2 != "":
              answer2 = x[y-1]
              if answer2 == answer:
                 break
              else:
                 for e in range (q,y,1):
                    array.append(x[e])
	      break
         elif y == index-1 and epoch2 != "" and counter-1 == len(m):
              answer2 = x[y]
              print "end of index answer is :", answer2
              for e in range (q,y,1):
                    array.append(x[e])
              break
# if there is only one date directory and it contains only one file, it must be the answer
         if len(x) == 1 and len(m) == 1:
              array.append(x[y])
              break

print "retrieved file epoch date is: " + array[0]

# set the length of the answer array
tLen=len(array)
print "retrieved last file epoch date is: " + array[tLen-1]
print "Answer Array Length is: " , tLen

# create an initial dummy pcap file for the merge process
call(["tcpdump", "-r", "/opt/sonion/empty.pcap", "-w", "/tmp/" + host + "_" + epoch + "tmp.pcap"])

# Create an array from the Filter string
FILTERS = sys.argv[3]     
FILTERS=FILTERS.split('-')

# see if freeform filter was entered and set FIL accordingly
if FILTERS[0] == "BPF":
	  CFILTER = sys.argv[3].translate(None, 'BPF')
	  FIL = CFILTER.replace('-',' ')

# otherwise follow the standard filter creation process
else:

	# break both the IP's and Ports by the + delimeter and make them both arrays as well
	FILTERIP=FILTERS[0].split('+')
	FILTERPRT=FILTERS[1].split('+')

	def FilterBPF(item,obj):
	   # Remove null values
	   #print "item is: " + str(item)
	   item=filter(None, item)

	   # construct the BPF based on the length of the arrays
	   if len(item) == 0:
	       return ""
	   elif len(item) == 1:    
	       return obj+" " + "".join(item)
	       print "FIL= " + FIL
	   elif len(item) == 2: 
	       return obj+" " + item[0] + " and " + item[1]  
	       print "FIL= " + FIL

	FIL=FilterBPF(FILTERIP,"host")   
	FILP=FilterBPF(FILTERPRT,"port")        
	  
	# determine if an "and' is required to split the IP and Ports if the variables aren't null
	if  FIL and FILP :
	    FIL=FIL + " and " + FILP
	else: 
	    FIL=FIL + FILP

print "FILTER: " + FIL              
# open the SO pcap answer files using the previously created BPF and merge them together 
for i in range (0, tLen):
   CAPDIR = str(time.strftime('%Y-%m-%d', time.localtime(float(array[i]))))
   call(["tcpdump", "-r", "/nsm/sensor_data/" + sodir + "/dailylogs/" + CAPDIR + "/snort.log." + array[i], "-w", "/tmp/" + host + "_" + epoch + "_" + str(i) + ".pcap", FIL]) 
   call(["mergecap", "-w", "/tmp/" + host + "_" + epoch + ".pcap", "/tmp/" + host + "_" + epoch + "tmp.pcap", "/tmp/" + host + "_" + epoch + "_" + str(i) + ".pcap"]) 
   call(["cp", "/tmp/" + host + "_" + epoch + ".pcap", "/tmp/" + host + "_" + epoch + "tmp.pcap"])

print "File Size is: "
call(["ls", "-lah", "/tmp/" + host + "_" + epoch + ".pcap"])
print "Pcap File Generated!"
