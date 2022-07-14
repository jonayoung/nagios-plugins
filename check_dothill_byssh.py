#!/usr/bin/env python

#   Copyright: Jona Young 2022,
#   Original Script Copyright Chris Cowley 2010
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
# Standard Nagios return codes
OK       = 0
WARNING  = 1
CRITICAL = 2
UNKNOWN  = 3

import sys
import telnetlib
from pexpect import pxssh
import string, re
import os
from optparse import OptionParser

__author__      = "Jona Young"
__title__       = "Nagios plugin to check Dot Hill Revolution Storage Arrays by SSH"
__version__     = 0.2


def parseOptions():
    parser = OptionParser()
    parser.add_option("-H", "--host", dest="HOST")
    parser.add_option("-U", "--username", dest="USERNAME")
    parser.add_option("-P", "--password", dest="PASSWORD")
    parser.add_option("-T", "--test", dest="TEST")
    (options, args) = parser.parse_args()

    global host, user, password, test
    host = options.HOST
    user = options.USERNAME
    password = options.PASSWORD
    test = options.TEST

def usage():
    print "Usage: \n"
    print "check_dothill -U <user> -H <host> -P <password> -T disk|vdisk|sensor-status|ports"

def checkSensors():
    error = 0
    ssh = pxssh.pxssh()
    ssh.login(host,user,password,auto_prompt_reset=False)
    ssh.sendline('show sensor-status')
    ssh.prompt()
    output = ssh.before.split("\r\n")
    for line in output:
        if line.find('Error') != -1:
            error = 1
    return error
                
def checkVdisks():
    error = 0
    #tn = telnetlib.Telnet(host)
    #tn.read_until("login: ")
    #tn.write(user + "\n")
    #tn.read_until("Password: ")
    #tn.write(password + "\n")
    #tn.write("show vdisks\n")
    #tn.write("exit\n")
    ssh = pxssh.pxssh()
    ssh.login(host,user,password,auto_prompt_reset=False)
    ssh.sendline('show vdisks')
    ssh.prompt()
    output = ssh.before.split("\n")
    for line in output:
        if line.find('Crit') != -1:
            error = 1
    return error

def checkPorts():
    error=0
    #tn = telnetlib.Telnet(host)
    #tn.read_until("login: ")
    #tn.write(user + "\n")
    #tn.read_until("Password: ")
    #tn.write(password + "\n")
    #tn.write("show ports\n")
    #tn.write("exit\n")
    ssh = pxssh.pxssh(timeout=10)
    ssh.login(host,user,password,auto_prompt_reset=False)
    ssh.setwinsize(100,1000)  
    ssh.sendline('set cli-parameters console pager disabled')
    ssh.prompt()
    ssh.sendline('show ports')
    ssh.prompt()
    output = ssh.before.split("\n")
    for line in output:
        if line.find('iSCSI') and line.find('Disconnected') != -1:
            print line
            error = error + 1
    return error

def checkDisks():
    error=0
    ssh = pxssh.pxssh(timeout=10)
    ssh.login(host,user,password,auto_prompt_reset=False)
    #important to eliminate excess line wrapping and tricky matching
    ssh.setwinsize(100,1000)
    ssh.sendline('set cli-parameters console pager disabled')
    ssh.prompt()
    ssh.sendline('show disks')
    ssh.prompt()
    output = ssh.before.split("\r\n")
    for line in output:
        #if a line contains GB it is probably a disk so look for the OK value (or not)
        if line.find("GB") and line.find('OK') != -1:
            error = error + 1
    return error

if __name__ == "__main__":
    parseOptions()
    if test == "sensor-status":
        if checkSensors() == 0:
            print "SENSORS OK"
            sys.exit(0)
        else:    
            print "SENSOR WARNING"
            sys.exit(1)
    elif test == "vdisks":
        if checkVdisks() == 0:
            print "vDisks OK"
            sys.exit(0)
        else:
            print "vDisk WARNING"
            sys.exit(1)

    elif test == "ports":
        if checkPorts() > 3:
            print "FC PORTS CRITICAL: All FC ports are down"
            sys.exit(2)
        elif checkPorts() <= 3 and checkPorts() > 0:
            print "FC PORT WARNING: %d ports are down" % checkPorts()
            sys.exit(1)
        else:
            print "FC PORTS OK"
            sys.exit(0)
            
    elif test == "disks":
        if checkDisks() > 1:
            print "DISK CRITICAL: Multiple disk failures"
            sys.exit(2)
        elif checkDisks() == 1:
            print "Disk WARNING: A disk has failed" 
            sys.exit(1)
        else:
            print "Disks OK"
            sys.exit(0)
    else:
        print "Unknown check! Available checks are:\nvdisks\nsensor-status\nports"
        sys.exit(22)
