# Creates a client-server network using Noah Anderson's Distributed Computing Framework 
# Keys stored in ~/.boto
import boto.ec2		# To connect to the cloud
import time		# To impose delays for startup
import paramiko     # To ssh to the cloud in a purely python way
import os		# Debuging
import sys		# Debuging

# Default values to write to new config files
# You can change these
DEBUG = False
REGION = "us-east-1"
SERVER_AMI_ID = "ami-7cd0eb14"
CLIENT_AMI_ID = SERVER_AMI_ID
KEYNAME = "NCF_Autofit"
KEYFILENAME = "/home/aolinger/Desktop/NCF_Autofit.pem"
SERVER_INSTANCE_TYPE = "t2.micro"
CLIENT_INSTANCE_TYPE = "t2.micro"
SECURITY_GROUP_IDS = ["sg-f43f7a90"] # Recommended that you change this to a secure group
USERNAME = "ubuntu"
NUMBER_OF_CLIENTS=1

# Don't change these (unless you know what you're doing)
CLIENT_PATH = "~/client/"
SERVER_PATH = "~/server/"

class distNet:
	def __init__(self, debug, region, server_ami_id, client_ami_id, keyname, keyfilename, server_instance_type, client_instance_type, security_group_ids, username, number_of_clients, client_path, server_path):
		self.debug=debug
		self.region=region
		self.server_ami_id=server_ami_id
		self.client_ami_id=client_ami_id
		self.keyname=keyname
		self.keyfilename=keyfilename
		self.server_instance_type=server_instance_type
		self.client_instance_type=client_instance_type
		self.security_group_ids=security_group_ids
		self.username=username
		self.number_of_clients=number_of_clients
		self.client_path=client_path
		self.server_path=server_path


	def ask_config(self):
		"""Asks user if they'd like to change the default settings"""
		print "These are the current settings:"
		print "\tdebug = %s\n\tregion = %s\n\tserver_ami_id = %s\n\tclient_ami_id = %s\n\tkeyname = %s\n\tkeyfilename = %s\n\tserver_instance_type = %s\n\tclient_instance_type = %s\n\tsecurity_group_ids = %s\n\tusername = %s\n\tnumber_of_clients = %s"%(self.debug,self.region, self.server_ami_id, self.client_ami_id, self.keyname, self.keyfilename, self.server_instance_type, self.client_instance_type, str(self.security_group_ids), self.username, str(self.number_of_clients))
		ans=False
		while(ans != 'yes' and ans != 'no'):
			if ans:
				print "Please type 'yes' or 'no'"
			ans=raw_input("\nUse these settings? (yes/no): ")
			ans=ans.lower()
		if ans == 'yes':
			self.run_setup()
		elif ans == 'no':
			self.run_cfg()
		else:
			print "Unexpected line execution"
			raise RuntimeError

	def run_cfg(self):
		"""Set connection variables"""
		msg = "%s is currently set to %s.\nLeave blank to keep old value or else type in a new value: "
		# DEBUG
		user_in = raw_input(msg%("DEBUG", str(self.debug)))
		if user_in == "":
			pass
		else:
			while(user_in != 'True' and user_in != 'False' and user_in != ""):
				print "Must type 'True', 'False', or leave blank"
				user_in = raw_input(msg%("DEBUG", self.debug))
			if user_in == "":
				pass
			elif user_in == "True":
				self.debug = True
			elif user_in == "False":
				self.debug = False
			else:
				print "Unexpected line execution"
				raise RuntimeError
		# REGION
		user_in = raw_input(msg%("REGION", self.region))
		if user_in == "":
			pass
		else:
			self.region = user_in
		# SERVER_AMI_ID
		user_in = raw_input(msg%("SERVER_AMI_ID", self.server_ami_id))
		if user_in == "":
			pass
		else:
			self.server_ami_id = user_in
		# CLIENT_AMI_ID
		user_in = raw_input(msg%("CLIENT_AMI_ID", self.client_ami_id))
		if user_in == "":
			pass
		else:
			self.client_ami_id = user_in
		# KEYNAME
		user_in = raw_input(msg%("KEYNAME", self.keyname))
		if user_in == "":
			pass
		else:
			self.keyname = user_in
		# KEYFILENAME
		user_in = raw_input(msg%("KEYFILENAME", self.keyfilename))
		if user_in == "":
			pass
		else:
			self.keyfilename = user_in
		# SERVER_INSTANCE_TYPE
		user_in = raw_input(msg%("SERVER_INSTANCE_TYPE", self.server_instance_type))
		if user_in == "":
			pass
		else:
			self.server_instance_type = user_in
		# CLIENT_INSTANCE_TYPE
		user_in = raw_input(msg%("CLIENT_INSTANCE_TYPE", self.client_instance_type))
		if user_in == "":
			pass
		else:
			self.client_instance_type = user_in
		# SECURITY_GROUP_IDS
		user_in = raw_input(msg%("SECURITY_GROUP_IDS", self.security_group_ids))
		if user_in == "":
			pass
		else:
			self.security_group_ids = list(user_in)
		# USERNAME #
		user_in = raw_input(msg%("USERNAME", self.username))
		if user_in == "":
			pass
		else:
			self.username = user_in
		# NUMBER_OF_CLIENTS
		user_in = raw_input(msg%("NUMBER_OF_CLIENTS", str(self.number_of_clients)))
		if user_in == "":
			pass
		else:
			while(not user_in.isdigit() and user_in != ""):
				print "Must type a valid integer or leave blank"
				user_in = raw_input(msg%("NUMBER_OF_CLIENTS", self.number_of_clients))
			if user_in == "":
				pass
			else:
				self.number_of_clients = int(user_in)

		# Confirmation
		print "Current settings are now:"
		print "\tdebug = %s\n\tregion = %s\n\tserver_ami_id = %s\n\tclient_ami_id = %s\n\tkeyname = %s\n\tkeyfilename = %s\n\tserver_instance_type = %s\n\tclient_instance_type = %s\n\tsecurity_group_ids = %s\n\tusername = %s\n\tnumber_of_clients = %s"%(self.debug,self.region, self.server_ami_id, self.client_ami_id, self.keyname, self.keyfilename, self.server_instance_type, self.client_instance_type, str(self.security_group_ids), self.username, str(self.number_of_clients))

		user_in=False
		while(user_in!= 'yes' and user_in != 'no'):
			if user_in:
				print "Please type 'yes' or 'no'" 
			user_in = raw_input("Are these settings correct?(yes/no)")
			user_in = user_in.lower()

		if user_in == 'yes':
			self.run_setup()

		elif user_in == 'no':
			print "Re-running config dialogue...\n"
			return self.run_cfg()
		else: 
			print "Unexpected line execution"
			raise RuntimeError

	def run_setup(self):
		boto_client = boto.ec2.connect_to_region(self.region)	        # Region
		# Server
		serverReservation = boto_client.run_instances(self.server_ami_id,	# Ami image ID
		min_count = 1,				                                		# Launch specific number of instances.
		max_count = 1,				                                		# 1 for the server
		key_name = self.keyname,					                		# key name
		instance_type = self.server_instance_type,				    		# Type of instance
		security_group_ids = self.security_group_ids)		        		# List of secutity group ID(s)
		# Client
		try:
		    clientReservation = boto_client.run_instances(self.client_ami_id,	# Ami image ID
		    min_count = self.number_of_clients,				                	# Launch specific number of instances.
		    max_count = self.number_of_clients,				                
		    key_name = self.keyname,							            	# key name
		    instance_type = self.client_instance_type,                       	# Type of instance
		    security_group_ids = self.security_group_ids)                    	# List of secutity group ID(s)
		except:
		    print "Could not make request for clients. Closing server connection..."
		    boto_client.terminate_instances(serverReservation.instances[0].id)
		    raise

		distserver_key = "horospicywolf"
		print "Waiting for instances to start"
		inst = list(serverReservation.instances+clientReservation.instances)
		# Wait for our instance to start running
		pending = list(inst)
		time.sleep(1) # Sometimes run into error making an update request before the request has been processed
		while len(pending) > 0:
		    for n in pending:
		        if n.update() == 'running':
		            print "Instance Running: %s@%s"%(self.username,n.ip_address)
		            pending.remove(n)
		            break
		    time.sleep(0.25)
		print "All instances running. Server at %s"%(inst[0].ip_address)
	
		# SSH Setup
		miko_client = []
		for i in range(len(inst)):
		    miko_client.append(paramiko.client.SSHClient())
		    miko_client[i].set_missing_host_key_policy(paramiko.AutoAddPolicy())

		# Debug
		if self.debug:
		    print "DEBUG variable info:\ncwd:"
		    time.sleep(1)
		    os.system('pwd')
		    print "ip address(server):", str(inst[0].ip_address)
		    print "username: ", self.username
		    print "KEYFILENAME: ", self.keyfilename

		#!! must wait for a time for connection to "firm up" or else you will get:
		# "socket.error: [Errno 111] Connection refused"
		# 25 seconds is not long enough, 30 seconds sometimes works, 40 seconds seems to work every time
		print "Allowing connection to process (takes ~40 seconds, may vary for different instance types)"
		time.sleep(40)

		i = 0
		err_count=0
		server_conf='{"host":"'+str(inst[0].ip_address)+'","port":9933,"servername":"MicroUbuntu","serverdetail":"UbuntuMicro instance on amazon cloud"}'

		while i < len(inst):
		    connected=True
		    print "Trying to connect to %s@%s..."%(self.username, inst[i].ip_address) 
		    try:
			# Try to connect
		        miko_client[i].connect(inst[i].ip_address, username=self.username, key_filename=self.keyfilename)
		    except:
		        if err_count < 10:
		            err_count+=1
		            print "Encountered an error, trying again. Attempt #%i"%(err_count)
		            time.sleep(10)
		            connected=False

		        else:
		            print "Encountered too many errors. Closing connection to %s@%s\nError message:%s\n"%(self.username,inst[i].ip_address,sys.exc_info()[0])
		            #miko_client[i].close()
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
		            init_server = "sudo ~/webserver/bin/httpd"                               	# Start webserver
		            init_server += "\ncd "+self.server_path			                            # Get into the correct directory	
		            init_server += "\necho "+distserver_key+" > distserver.key"                 # Write key
		            init_server += "\nsudo perl distserver.pl"                                  # Start Server
		            channel.exec_command(init_server)						                    # Run command
		        else:
		            print "Creating client at %s..."%(inst[i].ip_address)
		            init_client = "cd "+self.client_path                                        # Get into the correct directory
		            init_client += "\necho '"+server_conf+"' > server.conf"                     # Write config
		            init_client += "\necho "+distserver_key+" > distserver.key"                 # Write key
		            init_client += "\nperl distclient.pl"                                       # Start Client
		            channel.exec_command(init_client)                                           # Run command

		        i+=1
		print "Finished running commands"
		print "\n================================"
		print "Your server is at: %s\nKey: %s"%(str(inst[0].ip_address), distserver_key)
		print "================================\n"
		closeUp=False
		helpInfo = \
		"""
		======================================================
		Options:
		exit --close out all connections (terminate instances)
		wipe --clears client memory (will crash clients)
		help --prints this dialogue
		====================================================== 
		"""
		err_count = 0
		user_in = None
		while(user_in != 'exit'):
		    user_in=raw_input("Command: ")
		    if user_in == 'wipe':   #FIXME Currently breaks clients
		        i=1
		        while(i<len(inst)): #TODO rewrite to avoid code duplication
		            transport = miko_client[i].get_transport()
		            channel = transport.open_session()
		            print "Deleting tmp files of %s..."%(inst[i].ip_address)
		            cmd = "rm /tmp/distclient-temp*/* /tmp/distclient-temp*/temp/*"	            # Remove client files
		            channel.exec_command(cmd)	                                            	# Run command
		            channel.close()					                                        
		            i+=1

		    elif user_in == 'exit':
		        pass
		    elif user_in == 'help':
		        print helpInfo
		    else:
		        print "Input not understood\n",helpInfo
		
		
		# Close up
		inst_ids=[]
		for n in inst:
		    inst_ids.append(n.id)
		boto_client.terminate_instances(inst_ids)
		print "Connections closed"

def main(defaults):
	"""Creates instances"""
	settings=['debug','region','server_ami_id','client_ami_id','keyname','keyfilename','server_instance_type','client_instance_type','security_group_ids','username','number_of_clients', 'client_path', 'server_path']
	# Check for config file
	if not os.path.isfile("./distNetConfig.txt"):
		print "Did not find a config file. Generating a default configuration file as distNetConfig.txt."
		fh=open("distNetConfig.txt", 'w+')
		if len(settings) == len(defaults):
			for i in range(len(settings)):
				configLine = settings[i]+' = '+str(defaults[i])+'\n'
				fh.write(configLine)
			fh.close()
		else:
			raise ValueError("'defaults' list length does not match 'settings' list length")
	# Load settings
	fh=open("distNetConfig.txt")
	for configLine in fh: 																	# Reads through config file and assigns variables used to initialize distNet
		words=configLine.strip().split(' ')
		if words[0] in settings and words[1] == '=' and len(words) == 3:
			if words[0] in ['debug', 'security_group_ids', 'number_of_clients']:
				cmd = words[0]+' = '+words[2]
				exec(cmd)
			else:
				cmd = words[0]+' = "'+words[2]+'"'
				exec(cmd)

	# Report configuration settings and check for valid file.
	try:
		myNetwork = distNet(debug, region, server_ami_id, client_ami_id, keyname, keyfilename, server_instance_type, client_instance_type, security_group_ids, username, number_of_clients, client_path, server_path)
	except  NameError:
		print "\nConfig file did not initialize settings correctly. Please fix or delete the current config file and try again.\n"
		raise
	myNetwork.ask_config()

if __name__ == '__main__':
    main([DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS, CLIENT_PATH, SERVER_PATH])
