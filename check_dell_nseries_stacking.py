import netsnmp
import argparse
import sys
import numpy

parser = argparse.ArgumentParser()
parser.add_argument("--hostname",help="Hostname of the Switch",required=True)
parser.add_argument("--community",help="SNMP Community to connect with",required=True)
parser.add_argument("--version",help="SNMP Version",default=2)
parser.add_argument("--verbose",help="Enable Verbose output",default=0)

params = parser.parse_args()

stacking_status = netsnmp.VarList(netsnmp.Varbind('iso.3.6.1.4.1.674.10895.5000.2.6132.1.1.13.2.2.1.6'))
netsnmp.snmpwalk(stacking_status,Version = params.version,DestHost=params.hostname,Community = params.community)


status_array = []
output_string = ""

for unit in stacking_status:
	#print(unit.tag)
	#split oid on . character
	oid_parts = str(unit.tag).split('.')
	unit_number = oid_parts[18]
	unit_status = int(unit.val)
	if(unit_status == 1):
		status_array.append(0)
		output_string = output_string + " | Unit "+unit_number+" is Master"
	elif(unit_status == 2):
		output_string = output_string + " | Unit "+unit_number+" is Standby"
		status_array.append(0)
	elif(unit_status == 3):
		output_string = output_string + " | Unit "+unit_number+" is missing or broken"
		status_array.append(2)
	else:
		output_string = output_string + " | Unit "+unit_number+" is in unknown state"
		status_array.append(3)
	#print(unit_number)
	#print(int(unit.val))

#set the out status to be the maximum value of the array which should be the "worst" status
if len(status_array) == 0:
	print("UNKNOWN - No Data returned")
	sys.exit(3)
else:
	exit_status = int(numpy.amax(status_array))

if(exit_status == 0):
	print("OK - "+output_string.strip(" |"))
elif(exit_status == 2):
	print("CRITICAL - "+output_string.strip(" |"))
else:
	print("UNKNOWN - "+output_string.strip(" |"))
sys.exit(exit_status)
