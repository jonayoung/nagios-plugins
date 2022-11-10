# nagios-plugins
Nagios Plugins written by Jona Young

##  check_dothill_byssh.py
A plugin to check the health of a Dothill SANs and by extension the re-badged Dell EMC ME4024 Storage array and possibly some HP MSA storage arrays.

Built on the Telnet version available at https://github.com/chriscowley/nagios-tools

Usage Syntax:
```
python2 check_dothill_byssh.py -H 163.1.55.227 -T disks -U <login_username> -P <login_password>
```

##  check_dell_nseries_stacking.py
A plugin to check the stacking health of Dell N series campus switches as reported via SNMP, tested on an N1548.

Requires system libsnmp-dev

And python modules: python3-netsnmp, sys, argparse, numpy

Syntax:
```
python3 check_dell_nseries_stacking.py --hostname <hostip> --community <snmpcommunity>
```
##  check_dell_nseries_stacking_portstatus.py
A plugin to check the stacking port status of Dell N series campus switches as reported via SNMP, tested on an N1548. Allows a status to be raised for a partially degraded stack - e.g. one of the pair of stacking cables unplugged

Requires system libsnmp-dev

And python modules: python3-netsnmp, sys, argparse

Syntax:
```
python3 check_dell_nseries_stacking_portstatus.py --hostname <hostip> --community <snmpcommunity>
```
