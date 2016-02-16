import os
import argparse
import sys
import pexpect
parser = argparse.ArgumentParser()
parser.add_argument("--hostname",help="Hostname of the access point",required=True)
parser.add_argument("--username",help="Username of the access point",default="admin")
parser.add_argument("--password",help="Password of the access point",required=True)
parser.add_argument("--warning",help="Warning CPU level",required=True)
parser.add_argument("--critical",help="Critical CPU level",required=True)
params = parser.parse_args()

try:
    child = pexpect.spawn("ssh -o StrictHostKeyChecking=no admin@"+params.hostname)
    child.expect("password:")
    child.sendline(params.password)
    child.expect("#")
    child.sendline("show cpu detail")
    child.expect("#")
    cpu_output_raw = child.before
    cpu_output = cpu_output_raw.split('\r\n')
    child.sendline("exit")
    child.expect(pexpect.EOF, timeout=5)
except pexpect.exceptions.TIMEOUT:
    timeout = True

cpu_id = ""
cpu_list = []


for line in cpu_output:
	#print line
	if "CPU0 utilization:" in line:
		cpu_id = "0"
	if "CPU1 utilization:" in line:
		cpu_id = "1"
	if cpu_id != "" and "CPU total utilization" in line:
		cpu_list.append(line.replace(" ","").replace("CPUtotalutilization:","").replace('%',''))
 

for (cpu_id, load) in enumerate(cpu_list):
	#print str(cpu_id)+" : "+loadi
	int_load = load.split('.')[0]
	if int(int_load) > int(params.critical):
		print "CRITICAL - CPU "+str(cpu_id)+" Load: "+str(int_load)+"%"
		sys.exit(2)
	elif int(int_load) > int(params.warning):
		print "WARNING - CPU "+str(cpu_id)+" Load: "+str(int_load)+"%"
		sys.exit(1)
		
#If we get this far everything is ok!
print "OK - All CPUs within limits"
sys.exit(0)
