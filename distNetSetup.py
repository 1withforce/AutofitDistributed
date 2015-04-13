# Creates a client-server network using Noah Anderson's Distributed Computing Framework 
# Keys stored in ~/.boto
import boto.ec2	# To connect to the cloud
import time	# To impose delays for startup
import paramiko # To ssh to the cloud in a purely python way
import os 	# Debuging
import sys 	# Debuging

# You can change these
DEBUG = False
REGION = "us-east-1"
AMI_ID = "ami-882904e0"
KEYNAME = "Autofit Key Pair"
KEYFILENAME = "/home/aolinger/EC2/AutofitKeyPair.pem"
INSTANCE_TYPE = "t2.micro"
SECURITY_GROUP_IDS = ["sg-25e39441"]
USERNAME = "ubuntu"
NUMBER_OF_CLIENTS=2

# Don't change these (unless you know what you're doing)
CLIENT_PATH = "~/slowsquare_setup/"
#INIT_SERVER = 'cd slowsquare_setup\nperl distserver.pl'
INIT_SERVER = 'cd slowsquare_setup\nsudo perl distserver.pl &'
#INIT_CLIENT = 'cd slowsquare_setup\nperl distclient.pl'
INIT_CLIENT = 'cowsay moo\ncowsay Error: client command not redefined!'

def ask_config(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS):
	"""Asks user if they'd like to change the default settings"""
	print "DEBUG: %s"%(DEBUG)
	ans=False
	while(ans != 'yes' and ans != 'no'):
		if ans:
			print "Please type 'yes' or 'no'"
		ans=raw_input("Use Default? (yes/no): ")
		ans=ans.lower()
	if ans == 'yes':
		main(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
	elif ans == 'no':
		run_cfg(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
	else:
		print "Unexpected line execution"
		raise RuntimeError

def run_cfg(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS):
	"""Set connection variables"""
	msg = "%s is currently set to %s.\nLeave blank to keep old value or else type in a new value: "
	# DEBUG
	user_in = raw_input(msg%("DEBUG", str(DEBUG)))
	if user_in == "":
		pass
	else:
		while(user_in != 'True' and user_in != 'False' and user_in != ""):
			print "Must type 'True', 'False', or leave blank"
			user_in = raw_input(msg%("DEBUG", DEBUG))
		if user_in == "":
			pass
		elif user_in == "True":
			DEBUG = True
		elif user_in == "False":
			DEBUG = False
		else:
			print "Unexpected line execution"
			raise RuntimeError
	# REGION
	user_in = raw_input(msg%("REGION", REGION))
	if user_in == "":
		pass
	else:
		REGION = user_in
	# AMI_ID
	user_in = raw_input(msg%("AMI_ID", AMI_ID))
	if user_in == "":
		pass
	else:
		AMI_ID = user_in
	# KEYNAME
	user_in = raw_input(msg%("KEYNAME", KEYNAME))
	if user_in == "":
		pass
	else:
		KEYNAME = user_in
	# KEYFILENAME
	user_in = raw_input(msg%("KEYFILENAME", KEYFILENAME))
	if user_in == "":
		pass
	else:
		KEYFILENAME = user_in
	# INSTANCE_TYPE
	user_in = raw_input(msg%("INSTANCE_TYPE", INSTANCE_TYPE))
	if user_in == "":
		pass
	else:
		INSTANCE_TYPE = user_in
	# SECURITY_GROUP_IDS
	user_in = raw_input(msg%("SECURITY_GROUP_IDS", SECURITY_GROUP_IDS))
	if user_in == "":
		pass
	else:
		SECURITY_GROUP_IDS = list(user_in)
	# USERNAME
	user_in = raw_input(msg%("USERNAME", USERNAME))
	if user_in == "":
		pass
	else:
		USERNAME = user_in
	# NUMBER_OF_CLIENTS
	user_in = raw_input(msg%("NUMBER_OF_CLIENTS", str(NUMBER_OF_CLIENTS)))
	if user_in == "":
		pass
	else:
		while(not user_in.isadigit() and user_in != ""):
			print "Must type 'True', 'False', or leave blank"
			user_in = raw_input(msg%("DEBUG", DEBUG))
		if user_in == "":
			pass
		else:
			NUMBER_OF_CLIENTS = int(user_in)

	# Confirmation
	settings="DEBUG: %s\nREGION: %s\nAMI_ID: %s\nKEYNAME: %s\nKEYFILENAME: %s\nINSTANCE_TYPE: %s\nSECURITY_GROUP_IDS: %s\nUSERNAME: %s\nNUMBER_OF_CLIENTS: %s"
	print "Current settings are:\n",settings%(str(DEBUG),REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,str(SECURITY_GROUP_IDS),USERNAME, str(NUMBER_OF_CLIENTS))
	user_in=False
	while(user_in!= 'yes' and user_in != 'no'):
		if user_in:
			print "Please type 'yes' or 'no'" 
		user_in = raw_input("Are these settings correct?(yes/no)")
		user_in = user_in.lower()
	if user_in == 'yes':
		main(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
	elif user_in == 'no':
		print "Re-running config dialogue...\n"
		return run_cfg(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
	else: 
		print "Unexpected line execution"
		raise RuntimeError


def main(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS):
	# Create instance
	# Can sometimes crash from random bad connection, should retry
	boto_client = boto.ec2.connect_to_region(REGION)	# Region
	reservation = boto_client.run_instances(AMI_ID,		# Ami image ID
	min_count = NUMBER_OF_CLIENTS+1,			# Launch specific number of instances.
	max_count = NUMBER_OF_CLIENTS+1,			# +1 for the server
	key_name = KEYNAME,					# key name
	instance_type = INSTANCE_TYPE,				# Type of instance
	security_group_ids = SECURITY_GROUP_IDS) 		# List of secutity group ID(s)
	print "Waiting for instances to start"

	inst = reservation.instances
	# Wait for our instance to start running
	pending = list(inst)
	while len(pending) > 0:
		for n in pending:
			if n.update() == 'running':
				print "Instance Running: %s@%s"%(USERNAME,n.ip_address)
				pending.remove(n)
				break
		time.sleep(2)
		
	print "All instances running. Server at %s"%(inst[0].ip_address)
	# SSH Setup
	miko_client = []
	for i in range(len(inst)):
		miko_client.append(paramiko.client.SSHClient())
		miko_client[i].set_missing_host_key_policy(paramiko.AutoAddPolicy())
	# Debug
	if DEBUG:
		print "DEBUG variable info:\ncwd:"
		time.sleep(1)
		os.system('pwd')
		print "ip address(server):", str(inst[0].ip_address)
		print "username: ", USERNAME
		print "KEYFILENAME: ", KEYFILENAME

	#!! must wait for a time for connection to "firm up" or else you will get:
	# "socket.error: [Errno 111] Connection refused"
	# 25 seconds is not long enough, 30 seconds sometimes works, 40 seconds seems to work every time
	print "Allowing connection to process (takes ~40 seconds, may vary for different instance types)"
	time.sleep(40)

	i=0
	err_count=0
	server_conf='{"host":"'+str(inst[0].ip_address)+'","port":9933,"servername":"MicroUbuntu","serverdetail":"UbuntuMicro instance on amazon cloud"}'

	while i < len(inst):
		connected=True
		print "Trying to connect to %s@%s..."%(USERNAME, inst[i].ip_address) 
		try:
			# Try to connect
			miko_client[i].connect(inst[i].ip_address, username=USERNAME, key_filename=KEYFILENAME)
		except:
			if err_count < 10:
				err_count+=1
				print "Encountered an error, trying again. Attempt #%i"%(err_count)
				time.sleep(10)
				connected=False
				
			else:
				print "Encountered too many errors. Closing connection to %s@%s\nError message:%s\n"%(USERNAME,inst[i].ip_address,sys.exc_info()[0])
				miko_client[i].close()
				boto_client.terminate_instances(instance_ids=[inst[i].id])
				print "Connections closed"
				raise
		if connected:
			print "Connection established!"
			transport = miko_client[i].get_transport()
			channel = transport.open_session()
			# Instance at index 0 is always the server
			if i == 0:
				print "Creating server at %s..."%(inst[i].ip_address)	 
				channel.exec_command(INIT_SERVER) 	# setup server
			else:
				print "Creating client at %s..."%(inst[i].ip_address)
				INIT_CLIENT = "echo '"+server_conf+"' > "+CLIENT_PATH+"server.conf\nperl "+CLIENT_PATH+"distclient.pl &"
				channel.exec_command(INIT_CLIENT)		# setup clients
			#for line in sshout.readlines():							# read output (will be chaotic!)
				#print line,
			#print "Closing connection to %s@%s"%(USERNAME,inst[i].ip_address)
			#miko_client.close()
			i+=1
	print "Finished running commands"
	print "\n================================\nYour server is at %s\n================================\n"%(str(inst[0].ip_address))
	raw_input("Press Enter to close connections")
	# Close up
	inst_ids=[]
	for n in inst:
		inst_ids.append(n.id)
	boto_client.terminate_instances(inst_ids)
	print "Connections closed"

if __name__ == '__main__':
	ask_config(DEBUG,REGION,AMI_ID,KEYNAME,KEYFILENAME,INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
	

