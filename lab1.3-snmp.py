#/usr/bin/env python

# import snmp_helper functions

from snmp_helper import snmp_extract, snmp_get_oid

# CONSTANTS
DEVICE_LIST = {                     # Define a dictionary of device names and their IP address (in this case the port is used in the lab)

    'pynet_rtr1' : '7961',
    'pynet_rtr2' : '8061'

}

IP_ADDRESS = '50.242.94.227'        # IP of the devicess (lab environment is not typical in real world)

SNMP_COMMUNITY = 'galileo'          # Define the SNMP comunity string to use

SNMP_DEVICES = ((IP_ADDRESS, SNMP_COMMUNITY, DEVICE_LIST.get('pynet_rtr1')), (IP_ADDRESS, SNMP_COMMUNITY, DEVICE_LIST.get('pynet_rtr2')))   # Tuple that contains the proper connection string for each device

OIDS = {

    'sysName' : '1.3.6.1.2.1.1.5.0',                                    # The sysName is the hostname on the device

    'sysDescr' : '1.3.6.1.2.1.1.1.0',                                   # Description of the device

    'sysUptime' : '1.3.6.1.2.1.1.3.0',                                  # Uptime of the device

    'ccmHistoryRunningLastChanged' : '1.3.6.1.4.1.9.9.43.1.1.1.0',      # Uptime when running config last changed  

    'ccmHistoryRunningLastSaved' : '1.3.6.1.4.1.9.9.43.1.1.2.0',        # Uptime when running config last saved (note any 'write' constitutes a save)

    'ccmHistoryStartupLastChanged' :  '1.3.6.1.4.1.9.9.43.1.1.3.0'      # Uptime when startup config last saved

}


def determine_run_start_sync_stat(run_change_time, start_save_time):
    if start_save_time == 0:                    # If ccmHistoryStartupLastChanged time stamp is 0 then the startup config has never been saved since booted and return NeverSaved
        return 'NeverSaved'
    elif start_save_time >= run_change_time:    # If ccmHistoryStartupLastChanged time stamp is greater than or equal the ccmHistoryRunningLastChanged then return ConfigSaved
        return 'ConfigSaved'
    elif start_save_time <= run_change_time:    # If ccmHistoryStartupLastChanged time stamp is less than or equal to the ccmHistoryRunningLastChanged then return ConfigNotSaved
        return 'ConfigNotSaved'
    else:                                       # All other scenarios are unknown
        return 'Unknown'

def convert_time_stamp(time_stamp_value):
    return int(time_stamp_value) / 100 / 3600

def main():
    debug = False
    for device in SNMP_DEVICES:
        snmp_data = snmp_get_oid(device, oid=OIDS.get('sysName'))
        sys_name = snmp_extract(snmp_data)
        snmp_data = snmp_get_oid(device, oid=OIDS.get('sysUptime'))
        sys_uptime = snmp_extract(snmp_data)
        snmp_data = snmp_get_oid(device, oid=OIDS.get('ccmHistoryRunningLastChanged'))
        run_change_time = snmp_extract(snmp_data)
        snmp_data = snmp_get_oid(device, oid=OIDS.get('ccmHistoryStartupLastChanged'))
        start_save_time = snmp_extract(snmp_data)
        if debug == True:
            print "*************"
            print "sys_name: " + sys_name
            print "uptime: " + str(convert_time_stamp(sys_uptime)) + " hrs"
            print "run_change_time: " + str(convert_time_stamp(run_change_time)) + " hrs"
            print "start_save_time: " + str(convert_time_stamp(start_save_time)) + " hrs"
            print "*************"
        if determine_run_start_sync_stat(run_change_time,start_save_time) == 'NeverSaved':
            print sys_name + ": Config has never been saved since booted."
        elif determine_run_start_sync_stat(run_change_time,start_save_time) == 'ConfigSaved':
            print sys_name + ": Config has been saved."
        elif determine_run_start_sync_stat(run_change_time,start_save_time) == 'ConfigNotSaved':
            print sys_name + ": Config has *NOT* been saved!"
        else:
            print sys_name + ": An unknown sync status was returned."

if __name__ == '__main__':
    main()

