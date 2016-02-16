import os
import sys
import pexpect
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--hostname",help="Hostname of the access point",required=True)
parser.add_argument("--username",help="Username of the access point",default="admin")
parser.add_argument("--password",help="Password of the access point",required=True)
parser.add_argument("--threshold",help="POE Threshold",required=True,default=30)
params = parser.parse_args()

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


try:
   #print "Connecting"
   child = pexpect.spawn("ssh -o StrictHostKeyChecking=no "+params.username+"@"+params.hostname)
   child.expect(".*password.*")
   child.sendline(params.password)
   child.expect("#")
   #print "Connected"
   child.sendline("show inline-power")
   child.expect("#")
   poe_output_raw = child.before
   poe_output = poe_output_raw.split('\r\n')  
except Exception:
   raise
   print "UNKNOWN - SSH ERROR"
   sys.exit(3)

total_budget = 0
total_actual = 0

for line in poe_output:
    line = line.strip()
    #Space W is the best matching string I can find
    if " W" in line:
	parts = line.split()
	#If first part is a number we have a stack
	if RepresentsInt(parts[0]):
		slot_number = parts[0]
		enabled = parts[1]
		state = parts[2]
		power_actual = parts[5]
		power_budget = parts[3]
	else:
	#otherwise a single switch
		slot_number = 1
		state = parts[0]
		power_budget = parts[1]
		power_actual = parts[3]
	
	if state != "Operational":
		print "CRITICAL - Problem with POE reporting on slot "+slot_number
		sys.exit(2)
	if int(power_actual)+int(params.threshold) > int(power_budget):
		print "CRITICAL - POE budget within "+str(params.threshold)+"W of exhaution on slot "+str(slot_number)
		sys.exit(2)
	total_budget = total_budget + int(power_budget)
	total_actual = total_actual + int(power_actual)


print "OK - Current POE Usage is "+str(total_actual)+"W of "+str(total_budget)+"W Budget"
sys.exit(0)
