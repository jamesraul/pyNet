#!/usr/bin/python env

from snmp_helper import snmp_extract, snmp_get_oid

community_string = 'string'
ip = '1.1.1.1'
router1 = (ip, community_string, '7961')
router2 = (ip, community_string, '8061')
routers = (router1,router2)
sysName = '1.3.6.1.2.1.1.5.0'
sysDescr = '1.3.6.1.2.1.1.1.0'
snmpOIDs = (sysName, sysDescr)

def snmp_get(r,s):
    get = snmp_get_oid(r,s)
    return snmp_extract(get)

print "-------------------------------------"

for r in routers:
    for s in snmpOIDs:
        print snmp_get(r,s) + "\n-------------------------------------"
