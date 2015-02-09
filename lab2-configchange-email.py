#/usr/bin/env python

from snmp_helper import snmp_extract, snmp_get_oid_v3

import pickle

import os.path

from email_helper import send_mail

from time import gmtime, strftime

SNMP_USERNAME = 'pysnmp'
SNMP_AUTH_KEY = 'mykey'
SNMP_ENCRYPT_KEY = 'mykey'
SNMP_USER_AUTH_ENCRYPT = (SNMP_USERNAME, SNMP_AUTH_KEY, SNMP_ENCRYPT_KEY)

DEVICE_LIST = {
	'pynet-rtr1': ('1.1.1.1', 7961), 
	'pynet-rtr2': ('1.1.2.1', 8061)
}

# only using the RunnginConfigLastChanged OID, potential future proofing
SNMP_OIDS = {
    'sysName' : '1.3.6.1.2.1.1.5.0',                                    # The sysName is the hostname on the device
    'sysUptime' : '1.3.6.1.2.1.1.3.0',                                  # Uptime-stamp of the device
    'RunningConfigLastChanged' : '1.3.6.1.4.1.9.9.43.1.1.1.0',      	# Uptime-stamp when running config last changed 
}

DEVICE_DATA_FILE = 'device_data.pkl'

DEBUG = False

# function to check to make sure a file exists
def check_for_existing_data_file(filename):

	if DEBUG: print "Checking for existing data file."
	
	if os.path.isfile(filename):
		return True

	else:
		return False


# function to load pickle data from a previsouly written file
def load_data(filename):

	file = open(filename, 'rb')
	
	loaded_data = pickle.load(file)

	file.close()

	if DEBUG: print "[load_data] Importing existing device data. " + str(loaded_data)

	return loaded_data

# function grabs SNMP OID data from devices
def get_device_data_from_snmp(snmp_device):

	snmp_data = snmp_get_oid_v3(snmp_device, SNMP_USER_AUTH_ENCRYPT, oid=SNMP_OIDS.get('RunningConfigLastChanged'))
	
	snmp_device_data = snmp_extract(snmp_data)
	
	if DEBUG: print "[get_device_data_from_snmp] SNMP Data retrieved. " + str(snmp_device_data)
	
	return snmp_device_data

# function to dump data to a pickle file for later use
def dump_to_file(filename, data_to_dump):
	
	file = open(filename, 'wb')
	
	pickle.dump(data_to_dump, file)
	
	file.close()
	
	if DEBUG: print "[dump_to_file] Data was dumped to file. " + str(data_to_dump)

# setup variables to use email_helper module
def send_email_out(subject, message):
	recipient = 'myemail@domain.com'
	subject = subject
	message = message
	sender = 'pynet@domain.com'
	send_mail(recipient, subject, message, sender)

'''
Main program logic
- check to see if there is a file with exsiting data.
- If there is no existing data file, then we can simply snmp get new data and dump it to file.
- if there is existing data, we need to load it in as *old data*
	- gather the *new data* and dump it to file
	- compare the *old data* with the *new data*
		- if the *new data* is different than the *old data* fire off an email function
		- if the data is the same then we're done
'''

def main():
	
	if check_for_existing_data_file(DEVICE_DATA_FILE) == True:
		
		# load in the previous device data using the load_data function and pickle file
		old_device_data = load_data(DEVICE_DATA_FILE)
	
		# create new data dictionary to put the new snmp data in
		new_device_data = {}
		
		# for the devices in the list populate the new_device_data dictionary using the get_device_data_from_snmp
		for device in DEVICE_LIST:

			new_device_data[device] = get_device_data_from_snmp(DEVICE_LIST[device])

		dump_to_file(DEVICE_DATA_FILE, new_device_data)

		# display some output with all the data.
		print "Comparing data:\n [OLD DATA] " + str(old_device_data) + "\n [NEW DATA] " + str(new_device_data)
		

		# loop through both the old and new  data dictionaries to compare the values.
		for run_config_value in old_device_data:

			if DEBUG: print "Device: " + run_config_value
			
			if old_device_data[run_config_value] == new_device_data[run_config_value]:
				print "%s has *not* changed." %run_config_value

			else:
				print "%s has changed." %run_config_value
				subject = "[Device Config Changed] Device: %s Timestamp: " %run_config_value + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " UTC"
				message = "Device: %s \n" %run_config_value + "Time detected: " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " UTC"
				# email details about the change.
				print "[send_email_out] Sending notification email."
				send_email_out(subject, message)
	
	
	# If no previous data was found we can just grab the new data and write it to file.
	elif check_for_existing_data_file(DEVICE_DATA_FILE) == False:
	
		new_device_data = {}
	
		for device in DEVICE_LIST:
			new_device_data[device] = get_device_data_from_snmp(DEVICE_LIST[device])
	
		dump_to_file(DEVICE_DATA_FILE, new_device_data)
	
	# catch all/else scenarios
	else:
		print "**ERROR** There was an error determining if the data file exsited, script failed."


if __name__ == '__main__':
	main()



