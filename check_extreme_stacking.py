import netsnmp
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--hostname",help="Hostname of the Switch",required=True)
parser.add_argument("--community",help="SNMP Community to connect with",required=True)
parser.add_argument("--version",help="SNMP Version",default=2)
parser.add_argument("--verbose",help="Enable Verbose output",default=0)

params = parser.parse_args()

stacking_status = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.1916.1.33.1'))
netsnmp.snmpwalk(stacking_status,Version = params.version,DestHost=params.hostname,Community = params.community)

#print stacking_status

stacking_enabled = int(stacking_status[0].val)

error_string = ""
warning_string = ""

if stacking_enabled:
	if params.verbose:
		print "Stacking Enabled"
	#Details of stacking Oid at http://www.oidview.com/mibs/1916/EXTREME-STACKING-MIB.html
	
	#Check stack health (is every stack port connected)
	#Assumes that you are using Loop Topology, not Daisy Chain
	stack_port_index = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.1916.1.33.3.1.1'))
	stack_port_status = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.1916.1.33.3.1.4'))
        netsnmp.snmpwalk(stack_port_index,Version = params.version,DestHost=params.hostname,Community = params.community)
        netsnmp.snmpwalk(stack_port_status,Version = params.version,DestHost=params.hostname,Community = params.community)
	port_count = 0
	for ports in stack_port_index:
		if params.verbose:
			print "Found a stack port ID - "+ports.val
		chassis = ports.val[:1]
		if params.verbose:
			print ports.val+" Located in Chassis "+chassis
		if params.verbose:
			print "Port State "+stack_port_status[port_count].val 
		if int(stack_port_status[port_count].val) != 1:
			error_string = error_string + "Stacking Port Down in Chassis "+chassis+"\n"
		#increment
		port_count = port_count + 1
	#Check stack setup
	slot_roles = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.1916.1.33.2.1.4'))
	netsnmp.snmpwalk(slot_roles,Version = params.version,DestHost=params.hostname,Community = params.community)
	slot1_role = int(slot_roles[0].val)
	bottom_slot_role = int(slot_roles[len(slot_roles)-1].val)
	#1 = Master, 2 = Slave, 3 = Backup
	if slot1_role != 1:
		warning_string = "Slot 1 not the Master\n"
	#if bottom_slot_role != 3:
	#	if params.verbose:
	#		print "Bottom Slot Role - "+str(bottom_slot_role)
	#	warning_string = warning_string + "Bottom Slot not the Backup\n"
	
	#Return status and string
	if error_string != "":
		print "CRITICAL - "+error_string.rstrip("\n")
		sys.exit(2)
	elif warning_string != "":
		print "WARNING - "+warning_string.rstrip("\n")
		sys.exit(1)
 	else:
		print "OK - Stacking Enabled and Healthy"
		sys.exit(0)

else:
	print "OK - Stacking Not Enabled"
	sys.exit(0)
