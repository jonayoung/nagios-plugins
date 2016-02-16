import os
import sys
import pexpect
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--hostname",help="Hostname of the access point",required=True)
parser.add_argument("--username",help="Username of the access point",default="admin")
parser.add_argument("--password",help="Password of the access point",required=True)
params = parser.parse_args()


try:
   #print "Connecting"
   child = pexpect.spawn("ssh -o StrictHostKeyChecking=no "+params.username+"@"+params.hostname)
   child.expect(".*password.*")
   child.sendline(params.password)
   child.expect("#")
   #print "Connected"
   child.sendline("show stacking")
   child.expect("#")
   stacking_output_raw = child.before
   #print stacking_output_raw
   stacking_output = stacking_output_raw.split('\r\n')  
except Exception:
   raise
   sys.exit(3)

#print stacking_output

master = 0
backup = 0
standby = 0
for line in stacking_output:
    line = line.strip()
    #print line
    if "Stack Topology" in line:
	stack_topology = line
    if "Active Topology" in line:
	active_topology = line
        if active_topology == "This node is not in an Active Topology":
            print "OK - No Stacking configured"
            sys.exit(0)
    if "00:" in line:
	node_params = line.split()
	mac = node_params[0]
 	slot = node_params[1]
	state = node_params[2]
	topo_state = node_params[3]
	flags = node_params[4]
	#Role count sanity check
	if topo_state == "Master":
		master = master + 1
	if topo_state == "Backup":
		backup = backup + 1
	if topo_state == "Standby":
		standby = standby +1
	if slot == 1 and topo_state != "Master":
		print "WARNING - Slot 1 is not the master"
		sys.exit(1)
	if state != "Active":
		print "WARNING Slot "+slot+ "is not active"
		sys.exit(1)


if master > 1:
	print "CRITICAL - More than 1 Master Node"
	sys.exit(2)
if backup == 0:
	print "WARNING - No Backup Node"
	sys.exit(1)
if stack_topology == "Stack Topology is a Daisy-Chain":
    print "WARNING - Stack Topology is Daisy-Chain Not Ring"
    sys.exit(1)

print "OK - Stack in Healthy State"
sys.exit(0)
