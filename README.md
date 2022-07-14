# nagios-plugins
Nagios Plugins written by Jona Young

##  check_dothill_byssh.py
A plugin to check the health of a Dothill SANs and by extension the re-badged Dell EMC ME4024 Storage array and possibly some HP MSA storage arrays.

Built on the Telnet version available at https://github.com/chriscowley/nagios-tools

Usage Syntax:
```
python2 check_dothill_byssh.py -H 163.1.55.227 -T disks -U <login_username> -P <login_password>
```
