#!/bin/python
import datetime
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--hostname",help="Short Hostname of the Switch",required=True)
parser.add_argument("--interval",help="Number of minutes to detect loop for",required=True)
parser.add_argument("--uplinks",help="Uplink ports to exclude",required=True)
parser.add_argument("--verbose",help="Enable Verbose output",default=0)
params = parser.parse_args()

uplink_ports = params.uplinks.split(",")

#First of all get the date
now = datetime.datetime.now()
#todays_date = str(now.year)+str(now.month)+str(now.day)
todays_date = now.strftime("%Y%m%d")

log_dir = '/var/log/HOSTS/'

#/var/log/HOSTS/Test-SW01/Test-SW01.20150804
log_file_location = log_dir+params.hostname+'/'+params.hostname+'.'+todays_date

if params.verbose:
	print "Log File Location: "+log_file_location

#error_string = ""
looped_ports =[]
try:
	logfile = open(log_file_location,"r")
except IOError:
	print "UNKNOWN - No Log File Exists at "+log_file_location
        sys.exit(3)
for line in logfile:
	if "LOOP DETECTED" in line:
		components = line.split()
		#print components
		date = components[1]+" "+components[0]
		port_in = components[15].strip("()")
		port_out = components[18].strip("()")
		time = components[2]
		event_time = datetime.datetime.strptime(components[2],'%H:%M:%S')
		time_diff = now - event_time
		minutes_since_event = time_diff.seconds//60
		if minutes_since_event < int(params.interval):
			looped_ports.append(port_in)
			looped_ports.append(port_out)
			
			#error_string = error_string + "\nport "+port_in
		#+" and "+port_out
logfile.close()

problem_ports = []
unique_looped_ports = list(set(looped_ports))
for port in unique_looped_ports:
    if port not in uplink_ports:
        problem_ports.append(port)


if problem_ports:
	port_string = ""
	#print "CRITICAL - Loop Detected within last "+params.interval+" minutes"
	for port in problem_ports:
		port_string = port_string+" "+str(port)
	print "CRITICAL - Loop Detected on ports "+port_string+" within last "+params.interval+" minutes"
	sys.exit(2)
else:
	print "OK - No Loops"
	sys.exit(0)
