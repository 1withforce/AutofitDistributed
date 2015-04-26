#!/usr/bin/python
#
# slowsquare.py - Example distributed computing distributor
#
"""
Distributed computing distributor 
modified to parse autofit data
"""

#TODO get some actual test data
TESTDATA=[['fit 1', 'fit 2', 'fit 3'], 'other data', 'some more data']

import asyncore, asynchat, socket, hashlib, urllib
import json, random

# Dependent Autofit packages 
import numpy

# Debugging
import os

# Python version of app; gzip compressed tar file created from the directory named '/all' 
APP_NAME = "autofitDist.app"

# Compute MD5 and URL of chosen app
def get_app_md5(filename):
    """Read FILENAME.md5"""
    md5fh = open(filename + ".md5", 'r')
    md5 = md5fh.readline().strip()
    md5fh.close()
    print "md5:",md5
    return md5

#APP_MD5 = get_app_md5(APP_NAME)
APP_MD5 = None # Defined when runAutofit called

#FIXME make_app.sh currently depends on a certain file structure
# Build apps with make_app.sh

def find_server():
    """
    Read server.conf and distserver.key files to locate server connection
    information (hostname, port number, password/key).
    """
    # Default information
    (host, port, key) = ("localhost", 9933, "couldnt_find_distserver.key")

    # Try loading hostname and port number from server.conf file
    try:
        conf_file = open('server.conf', 'r')
        print "Found a server config file!"
        obj = json.loads(conf_file.read(10240))
        if 'host' in obj:
            host = obj['host']
        if 'port' in obj:
            port = obj['port']
        conf_file.close()
    except IOError:
        pass

    # Try loading password from distserver.key file
    try:
        conf_file = open('distserver.key', 'r')
        key = conf_file.readline().strip()
        conf_file.close()
    except IOError:
        pass

    # Return the server information
    return (host, port, key)

class Distributor(asynchat.async_chat):
    """
    Class for communication with distributed computing server.
    Based on asynchat.async_chat.
    Implements the SlowSquare problem.
    """

    def __init__(self, (host, port, key), name, jobData, app_url):
        # Connect to the server
        print "Trying to connect to server",str(host),':',str(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        asynchat.async_chat.__init__(self, sock=sock)
        self.ibuffer = []
        self.set_terminator("\n")
        self.key = key      # distserver password
        self.name = name    # Workunit name prefix
        self.index = 0      # Sequential workunit number
        self.unsent = []    # Work that we've generated but not sent
        self.running = {}   # Work that we've sent but not heard back about
        self.app_url = app_url

        # Generate work
        xyzTransList = jobData[0]
        for i in xyzTransList:
            self.unsent.append([i]+jobData[1:])

    def collect_incoming_data(self, data):
        """
        Accumulate data read from the server.
        See asynchat.async_chat.collect_incoming_data.
        """
        self.ibuffer.append(data)

    def found_terminator(self):
        """
        Handle an individual line that has been read from the server.
        Parses the line and dispatches to an appropriate handler function.
        """
        # Parse line
        cmd = "".join(self.ibuffer).strip().split(None, 1)
        if len(cmd) < 2:
            cmd.append(None)
        cmd[0] = cmd[0].upper()
        self.ibuffer = []

        # Handle commands received from server
        if cmd[0] == "ERR":
            raise Exception, "ERR %s" % cmd[1]
        elif cmd[0] == "HELLO":
            self.push('HELLO 0 %s %s\n'%(self.name, self.key))
        elif cmd[0] == "NEWWORKER":
            self.check_for_work()   # Try to send work
        elif cmd[0] == "NOWORKERS":
            pass                    # Do nothing
        elif cmd[0] == "OK":
            self.check_for_work()
        elif cmd[0] == "WORKER":
            self.send_work(json.loads(cmd[1])) # Send this worker some work
        elif cmd[0] == "WORKACCEPTED":
            pass                    # Do nothing
        elif cmd[0] in ("WORKFINISHED", "WORKFAILED", "WORKREJECTED"):
            self.finished_work(cmd[0] == "WORKFINISHED", json.loads(cmd[1]))
            self.check_for_work()
        else:
            raise Exception, "Unknown command %s" % cmd[0]

    def request_worker(self):
        """
        Send a HAVEWORK command to the server to request a worker.
        """
        self.push('HAVEWORK\n')

    def dispatch(self, obj):
        """
        Send a DISPATCH command to the server to send a workunit (obj) to a
        worker computer.
        """
        self.push('DISPATCH %s\n' % json.dumps(obj))

        # See if we have more work to send
        self.check_for_work()

    def check_for_work(self):
        """
        Check if there is work to send.
        """
      
        # Check if we have work to send, and if so, request a worker
        if len(self.unsent) > 0:
            self.request_worker()   # Request more work
        elif len(self.running) == 0:
            self.close_when_done()  # All work finished; Close out program
        else:
            pass                    # Wait for work to complete
    
    def send_work(self, worker):
        """
        Package some work into a workunit.
        For SlowSquare, we pop a single item off of the unsent-items list.
        We then put the item on a list of workunits.
        This will need to be overridden to implement some other problem.
        Workunits should be designed to take ~10-60 seconds.
        """
        # Ensure there are unsent items to send
        if len(self.unsent) <= 0:
            return

        # Pop item from unsent queue
        item = self.unsent.pop()

        # Create workunit name
        self.index += 1
        name = "%s-%05d" % (self.name, self.index)

        # Move item to running list
        self.running[name] = item

        # Encode input file
        item_str = str(item) 
        item_md5 = hashlib.md5(item_str).hexdigest()
        item_url = "data:text/plain,%s" % (item_str)
	
	#testdoc=open('testdoc.txt', 'w')
	#testdoc.close()
	#os.system('scp -i ~/Desktop/NCF_autofit.pem ./testdoc.txt ubuntu@%s')	

        # Create object
        obj = {'id': name, 'duration': 20,
               'files': [[get_app_md5(APP_NAME), self.app_url, "autofitDist.app"],	
			 [item_md5, item_url, "temp/%s" % (name)]],                  
               'upload': 'data:', 'worker': worker['id']}
        
        # Send to worker
        print "Sending %s to %s" % (name, worker['name'])
        self.dispatch(obj)

    def finished_work(self, successful, obj):
        """
        Handle a completed workunit.
        The workunit may have been successful or not.
        If not, the work will need to be retried.
        For SlowSquare, put unsuccessful items back on the unsent-items list.
        Otherwise, display the squared value.
        This will need to be overridden to implement some other problem.
        """
        name = obj['id']
        if name not in self.running:
            print "%s: not running" % (name)
            # Got response for unknown workunit, ignore it
            return
        class WorkunitError(Exception):
            """
            Exception class for handling errors in the returned workunit.
            If raised, exception handler will return work to be retried.
            """
            pass
        try:
            if not successful or 'error' in obj:
                raise WorkunitError, "Error: %s" % \
                    (obj['error'] if 'error' in obj else 'Unknown')
            # Display result
            files = obj['files']
            if len(files) != 1:
                raise WorkunitError, "Wrong number of files returned"
            elif files[0][2].startswith('data:'): 
                try:
                    answer = str(urllib.urlopen(files[0][2]).read())
                except:
                    answer = 'unknown'
                    print "!! Problem with opening url\n"
                    raise WorkunitError, "Failed to decode data: URL"
                finally:
                    # Display the result
                    print "%s:\n%s" % (name, answer)
                    fh=open('sorted_final_out'+str(self.running[name][0][3])+'.txt', 'w')
                    fh.write(answer)
                    fh.close()
                    print "Completed a workunit. %i unsent, %i currently running"%(len(self.unsent), len(self.running))
            else:
                raise WorkunitError, "Only data: file locations are supported"
          
        except WorkunitError:
            # Mark item in workunit as incomplete, resend it later
            self.unsent.append(self.running[name])
        # Remove completed workunit
        del(self.running[name])

def getInfo(data, name='data'):
    """Debugging function for checking data arrays"""
    i = 0
    print "Dumping contents of %s..."%(name)
    while i < len(data):
        print "data[%i]:"%(i)                                                               # Index                              
        print "\ttype:",type(data[i]),"\n\tvalue:",                                         # Type
        if (type(data[i]) == list or type(data[i])==numpy.ndarray) and len(data[i]) > 5:    
            print data[i][:4],"..."                                                         # First four elements if long list
        else:
            print data[i]                                                                   # Every element otherwise
        i+=1

def runAutofit(jobData, app_url):
    """
    Create an instance of the distributor and run it forever.
    """
    server_app_url = app_url+APP_NAME
    numpy.save("../all/peaklist.npy", jobData.pop(5))
    os.system("sudo ../make_app.sh ../")
    os.system("scp -i ~/Desktop/NCF_Autofit.pem ../upload/autofitDist.app ubuntu@%s:~/webserver/htdocs/"%(app_url[7:-1]))
    print "APP_URL: "+app_url                                                         
    os.system('cp ../distserver.key ../autofitDist.app.md5 ../server.conf ./')                # Copy key from parent directory into current directory
    #APP_MD5 = get_app_md5(APP_NAME)
    #getInfo(jobData, 'jobData')
    #print "converting numpy ndarray to normal python list"
    #jobData[5] = jobData[5].tolist()
    # Create instance of the distributor
    Distributor(find_server(), "autofitDist", jobData, server_app_url)
    
    # Run it forever
    asyncore.loop()

if __name__ == '__main__':
    runAutofit(TESTDATA)

