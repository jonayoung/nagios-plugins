import netsnmp
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--hostname",help="Hostname of the Switch",required=True)
parser.add_argument("--community",help="SNMP Community to connect with",required=True)
parser.add_argument("--version",help="SNMP Version",default=2)
parser.add_argument("--verbose",help="Enable Verbose output",default=0)

params = parser.parse_args()

port_names = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.13.7.2.1.3'))
port_modes = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.13.7.2.1.4'))
port_stats = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.674.10895.5000.2.6132.1.1.13.7.2.1.6'))

netsnmp.snmpwalk(port_names,Version = params.version,DestHost=params.hostname,Community = params.community)
netsnmp.snmpwalk(port_modes,Version = params.version,DestHost=params.hostname,Community = params.community)
netsnmp.snmpwalk(port_stats,Version = params.version,DestHost=params.hostname,Community = params.community)

output_string = ""
stacking_error_count = 0

i = 0
for port in port_names:
	port_name = str(port.val).strip("'b")
	port_mode = int(port_modes[i].val)
	port_stat = int(port_stats[i].val)
	#port mode 1 = stacking, 2 = ethernet
	if port_mode == 1:
		# 1 = port up, 2 = port down
		if port_stat != 1:
			output_string = output_string + " | "+port_name+" is in stacking mode and not up"
			stacking_error_count = stacking_error_count + 1
	i = i + 1

if stacking_error_count == 0:
	print("OK - All configured stack ports are up")
	sys.exit(0)
elif stacking_error_count > 1:
	print("CRITICAL - "+output_string.strip(' |'))
	sys.exit(2)
else:
	print("UNKNOWN")
	sys.exit(3)
