#!/usr/bin/python3.6
import threading
import time
import socket
import sys
import re
import os


class portChecker(threading.Thread):
	def __init__(self,portNum):
		threading.Thread.__init__(self)
		self.portNum=portNum
	def __del__(self):
		''
		#print("deleting "+str(self.portNum))

	def run(self):
		while 1:
			try:
				sock=socket.socket()
				sock.settimeout(timeout)
				sock.connect((host, self.portNum))
				if verbose:
					sys.stderr.write(str(self.portNum)+" connected\n")
				else:
					print(self.portNum)
					sys.stdout.flush()
				sock.shutdown(socket.SHUT_RDWR)

			# if a firewall drops a connection (rather than actively refusing it), the socket will time out
			except socket.timeout:
				if verbose:
					sys.stderr.write(str(self.portNum)+" timed out\n")
					sys.stderr.flush()
				sock.shutdown(socket.SHUT_RDWR)

			# if a firewall refects a connection (rather than passively dropping it)
			except ConnectionRefusedError:
				if verbose:
					sys.stderr.write(str(self.portNum)+" refused\n")
					sys.stderr.flush()
				#sock.shutdown(socket.SHUT_RDWR)

			except socket.gaierror:
				# if the hostname is bad every thread will hit this block of code, so synchronize it then exit
				lock.acquire()
				sys.stderr.write("Bad hostname '"+host+"'\n"+str(socket.gaierror))
				sys.stderr.flush()
				os._exit(1)
				# won't hit this next line
				lock.release()
			except OSError as e:
				# too many threads are open, or
				lock.acquire()

				sys.stderr.write(str(time.time())+" too many files "+str(cnt)+","+str(startcnt)+"\n"+"error="+str(e)+"\n")
#				time.sleep(1)
				sys.stderr.flush()
				os._exit(1)
				# won't hit this next line
				lock.release()
			sock.close()
			break


def printUsage():
	print("\nUsage:\n\tportScan.py [ports] [host]\n\tportScan.py 1-10 tagput.com\n\tportScan.py 5 68.66.193.56")
	exit(1)

verbose=False
lock=threading.Lock()
st=time.time()

threads=[]
maxThreads=2000
finished=0
cnt=0
startcnt=0
timeout=1

# this block just gets all the command line options
try:
	index=1
	if sys.argv[index] == "-v":
		index=index+1
		verbose=True
		sys.stderr.write("verbose\n")

	ports=sys.argv[index]
	match=re.search('^(\d+)(-(\d+))?$',ports)
	if not match:
		printUsage()

	startPort=match.group(1)
	endPort=match.group(3)
	if endPort is None:
		endPort=startPort

	index=index+1
	host=sys.argv[index]
except IndexError:
	printUsage()

ports=range(int(startPort),int(endPort)+1)

while len(ports) > 0:
	#delete memory
	threads=[]
	# if there's more than maxThreads, scan maxThreads at a time
	these=ports[:maxThreads]
	ports=ports[maxThreads:]

	for port in these:
		thread=portChecker(port)
		thread.start()
		threads.append(thread)
		startcnt=startcnt+1

	# wait for all threads to finish
	for t in threads:
		t.join()
		del t
		cnt=cnt+1
	finished=finished+len(these)
	sys.stderr.write("scanned "+str(finished)+" ports\n")
	sys.stderr.flush()
et=time.time()
if verbose:
	sys.stderr.write("time="+str(et-st)+"\n")
