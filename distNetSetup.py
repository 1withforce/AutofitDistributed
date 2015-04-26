# Creates a client-server network using Noah Anderson's Distributed Computing Framework 
# Keys stored in ~/.boto
import boto.ec2		# To connect to the cloud
import time		# To impose delays for startup
import paramiko     # To ssh to the cloud in a purely python way
import os		# Debuging
import sys		# Debuging

#TODO read and write to a config file
# You can change these
DEBUG = False
REGION = "us-east-1"
SERVER_AMI_ID = "ami-7cd0eb14"
CLIENT_AMI_ID = SERVER_AMI_ID
KEYNAME = "NCF_Autofit"
KEYFILENAME = "/home/aolinger/Desktop/NCF_Autofit.pem"
SERVER_INSTANCE_TYPE = "t2.micro"
CLIENT_INSTANCE_TYPE = "t2.micro"
SECURITY_GROUP_IDS = ["sg-f43f7a90"]
USERNAME = "ubuntu"
NUMBER_OF_CLIENTS=1
APP_LOCATION="../upload/autofitDist.app"    #TODO Add to config dialogue

# Don't change these (unless you know what you're doing)
CLIENT_PATH = "~/client/"
SERVER_PATH = "~/server/"

def ask_config(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS):
	"""Asks user if they'd like to change the default settings"""
	print "DEBUG: %s"%(DEBUG)
	ans=False
	while(ans != 'yes' and ans != 'no'):
		if ans:
			print "Please type 'yes' or 'no'"
		ans=raw_input("Use default settings? (yes/no): ")
		ans=ans.lower()
	if ans == 'yes':
		main(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
	elif ans == 'no':
		run_cfg(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
	else:
		print "Unexpected line execution"
		raise RuntimeError

def run_cfg(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS):
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
	# SERVER_AMI_ID
	user_in = raw_input(msg%("SERVER_AMI_ID", SERVER_AMI_ID))
	if user_in == "":
		pass
	else:
		SERVER_AMI_ID = user_in
	# CLIENT_AMI_ID
	user_in = raw_input(msg%("CLIENT_AMI_ID", SERVER_AMI_ID))
	if user_in == "":
		pass
	else:
		CLIENT_AMI_ID = user_in
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
	# SERVER_INSTANCE_TYPE
	user_in = raw_input(msg%("SERVER_INSTANCE_TYPE", SERVER_INSTANCE_TYPE))
	if user_in == "":
		pass
	else:
		SERVER_INSTANCE_TYPE = user_in
	# CLIENT_INSTANCE_TYPE
	user_in = raw_input(msg%("CLIENT_INSTANCE_TYPE", CLIENT_INSTANCE_TYPE))
	if user_in == "":
		pass
	else:
		CLIENT_INSTANCE_TYPE = user_in
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
		while(not user_in.isdigit() and user_in != ""):
			print "Must type a valid integer or leave blank"
			user_in = raw_input(msg%("DEBUG", DEBUG))
		if user_in == "":
			pass
		else:
			NUMBER_OF_CLIENTS = int(user_in)

	# Confirmation
	settings="DEBUG: %s\nREGION: %s\nSERVER_AMI_ID: %s\nCLIENT_AMI_ID: %s\nKEYNAME: %s\nKEYFILENAME: %s\nSERVER_INSTANCE_TYPE: %s\nCLIENT_INSTANCE_TYPE: %s\nSECURITY_GROUP_IDS: %s\nUSERNAME: %s\nNUMBER_OF_CLIENTS: %s"
	print "Current settings are:\n",settings%(str(DEBUG),REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,str(SECURITY_GROUP_IDS),USERNAME, str(NUMBER_OF_CLIENTS))

	user_in=False

	while(user_in!= 'yes' and user_in != 'no'):
		if user_in:
			print "Please type 'yes' or 'no'" 
		user_in = raw_input("Are these settings correct?(yes/no)")
		user_in = user_in.lower()

	if user_in == 'yes':
		main(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)

	elif user_in == 'no':
		print "Re-running config dialogue...\n"
		return run_cfg(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)

	else: 
		print "Unexpected line execution"
		raise RuntimeError


def main(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS):
	# Create instance
	# Can sometimes crash from random bad connection, should retry

    boto_client = boto.ec2.connect_to_region(REGION)	        # Region
    # Server
    serverReservation = boto_client.run_instances(SERVER_AMI_ID,# Ami image ID
    min_count = 1,				                                # Launch specific number of instances.
    max_count = 1,				                                # 1 for the server
    key_name = KEYNAME,							                # key name
    instance_type = SERVER_INSTANCE_TYPE,					    # Type of instance
    security_group_ids = SECURITY_GROUP_IDS)		            # List of secutity group ID(s)
    # Client
    try:
        clientReservation = boto_client.run_instances(CLIENT_AMI_ID,# Ami image ID
        min_count = NUMBER_OF_CLIENTS,				                # Launch specific number of instances.
        max_count = NUMBER_OF_CLIENTS,				                
        key_name = KEYNAME,							                # key name
        instance_type = CLIENT_INSTANCE_TYPE,                       # Type of instance
        security_group_ids = SECURITY_GROUP_IDS)                    # List of secutity group ID(s)
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
                print "Instance Running: %s@%s"%(USERNAME,n.ip_address)
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

    i = 0
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
                #cmd = "scp -i %s %s %s@%s:~/webserver/htdocs/"%(KEYFILENAME,APP_LOCATION, USERNAME, inst[i].ip_address) #FIXME better way of doing this using boto
                #os.system(cmd)                                                              # Copy app FIXME Linux only
                init_server = "sudo ~/webserver/bin/httpd"                               # Start webserver
                init_server += "\ncd "+SERVER_PATH			                                # Get into the correct directory	
                init_server += "\necho "+distserver_key+" > distserver.key"                 # Write key
                init_server += "\nsudo perl distserver.pl"                                  # Start Server
                channel.exec_command(init_server)						                    # Run command
            else:
                print "Creating client at %s..."%(inst[i].ip_address)
                init_client = "cd "+CLIENT_PATH                                             # Get into the correct directory
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
    wipe --wipes the data from each client
    exit --close out all connections (terminate instances)
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
                cmd = "rm -r /tmp/distclient-temp*"                                     # Remove client folders
                channel.exec_command(cmd)	                                            # Run command
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

if __name__ == '__main__':
    ask_config(DEBUG,REGION,SERVER_AMI_ID,CLIENT_AMI_ID,KEYNAME,KEYFILENAME,SERVER_INSTANCE_TYPE,CLIENT_INSTANCE_TYPE,SECURITY_GROUP_IDS, USERNAME,NUMBER_OF_CLIENTS)
