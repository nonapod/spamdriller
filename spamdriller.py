#!/bin/env python
# :
# : spamdrill.py
# : Written by Les Cordell 
# :
# : This script will run through the /proc directory,
# : it will open up any directory matching a number,
# : it will then simply display requested output
#######################
_VERSION = "0.0.1"
_AUTHOR = "Les Cordell"
# : Imports : #
import sys, re, os, datetime

# : Timestamp Function : #
def sdr_timestamp():
	now = datetime.datetime.now();
	return str(now.year) + "-" + str(now.month) + "-" + str(now.day) + "-" + str(now.hour) + str(now.minute) + str(now.second)

# : Defaults : #
_DIRECTORY = "/proc"
_OUTPUT = "spamdrill_" + sdr_timestamp() + ".log"
_OUTPUTDIR = os.path.abspath("./")
_OPTIONS = {
				# : Available options; pgid, cwd, exe, root enabled by default
				"pgid": True, "uid": False,
				"cwd": True, "exe": True, "root": False, 
				"status": False, "maps": False
			}
_VALIDPROCDIRS = re.compile('^[0-9]+$') # Valid names for process directories i.e. 3313, 44412, 24323, 1123 they match the pid
_CR = "\n"


# If we're using Windows, then we'll set the carriage return character to \r\n
if os.name == "nt":
	_CR = "\r\n"


def spamdrill():
	# : Use the following global variables
	global _DIRECTORY
	global _OPTIONS
	global _OUTPUTDIR
	global _CR

	arglength = len(sys.argv)

	# : BANNER : #
	print "~~|> Spamdrill v" + _VERSION + " <|~~"
	print "Written by " + _AUTHOR + "\n"

	# : Commandline Arguements : #
	if arglength > 1:
		for idx, val in enumerate(sys.argv):
			############################
			# : DIRECTORY ARGUEMENT :  #	-d
			############################
			# If we get a directory selection and a value following it
			if val == "-d" and arglength > idx+1 and sys.argv[idx+1]:
				# Store the next index as the newdirectory 
				newdirectory = sys.argv[idx + 1] 
				# Check the directory is a valid directory and readable
				if os.path.exists(newdirectory):
					# If we have read permissions on the directory then we'll save and continue
					if os.access(newdirectory, os.R_OK):
						_DIRECTORY = os.path.abspath(sys.argv[idx+1])
					else:
						#If we can read the directory then we'll abort
						print "You do not have read permissions on " + newdirectory + " aborting..."
						quit()
				# If the directory is invalid, abort
				else:
					print "Invalid directory " + newdirectory + " aborting..."
					quit()

			################################
			# : OPTION ENABLE ARGUEMENTS : #	
			################################
			# -r -s -u -m -a -p -h -l  | root, status, uid, maps, all, print, help, logfile
			if val == "-r":
				_OPTIONS["root"] = True
			if val == "-s":
				_OPTIONS["status"] = True
			if val == "-u":
				_OPTIONS["uid"] = True
			if val == "-m":
				_OPTIONS["maps"] = True
			if val == "-w":
				_CR = "\r\n"
			# Print settings on a print command
			if val == "-p":
				print "Settings are: "
				for idx, opt in enumerate(_OPTIONS):
					print str(idx) + " " + str(opt).ljust(10) + " - ".ljust(5) + str(_OPTIONS[opt])
				quit()
			# Display help on an -h command
			if val == "-h":
				print "This script will traverse the appropriate proc directory and dump out as much"
				print "info as it can about all the running processes in hopes of catching a spam script."
				print "Spam scripts often fire off at quick intervals and vanish before you can look in the"
				print "proc directory, that's where this script comes in, it will grab all of this information"
				print "and dump it out into a file for you to check.\n"
				print "Available options are: "
				print "-d".ljust(5) + "specify alternate directory, default is /proc"
				print "-r".ljust(5) + "dump root application location"
				print "-s".ljust(5) + "dump process status"
				print "-u".ljust(5) + "dump uid"
				print "-m".ljust(5) + "dump maps"
				print "-a".ljust(5) + "dump all options"
				print "-p".ljust(5) + "show default options"
				print "-l".ljust(5) + "directory to output the logfile, default is current directory"
				print "".ljust(5)   + "the filename format is spamhk_(timestamp goes here here).log"
				print "-w".ljust(5) + "if you're using cygwin and want this to display in Windows"
				print "".ljust(5)	+ "then this option will use \\r\\n for carriage return instead of \\n"
				print "".ljust(5)	+ "NOTE: This does autodetect, but for Cygwin you will need this option."
				print "-h".ljust(5) + "show this help again"
				print "\n"
				quit()
			# Logfile location
			if val == "-l" and arglength > idx+1 and sys.argv[idx+1]:
				logdirectory = sys.argv[idx + 1]
				if os.path.exists(logdirectory):
					if os.access(logdirectory, os.W_OK):
						_OUTPUTDIR = os.path.abspath(sys.argv[idx+1])	
					# If the directory output path is not writable, abort
					else:
						print "Unable to write to this directory aborting..."
						quit()
				# If the directory doesn't exist, abort
				else:
					print "Directory does not exist for log output, aborting"
			# Set all options
			if val == '-a':
				_OPTIONS["root"] = True
				_OPTIONS["status"] = True
				_OPTIONS["uid"] = True
				_OPTIONS["maps"] = True


	
	# : BEGIN SPAMDRILL : #
	# First make sure the directory exists and is readable
	if os.path.exists(_DIRECTORY):
		if os.access(_DIRECTORY, os.R_OK):
			# We'll just pass here and continue the rest beneath the directory checks
			pass
		else:
			print "You do not have read permissions on " + _DIRECTORY + ", aborting..."
			quit()	
	else:
		print "Invalid directory " + _DIRECTORY 
		print "Specify the appropriate /proc directory or equivalent using the -d variable"
		print "i.e. spamhk.py -d /var/proc "
		print "aborting..."
		quit()	

	# Then make sure our log output directory is writable
	if os.path.exists(_OUTPUTDIR):
		if os.access(_OUTPUTDIR, os.W_OK):
			# We'll just pass here and continue the rest beneath the directory checks
			pass
		else:
			print "You do not have write permissions on " + _OUTPUTDIR + ", aborting..."
			quit()	
	else:
		print "Invalid log directory " + _OUTPUTDIR
		print "You specified an invalid log directory, leave the -l option blank to default to your current dir"
		print "aborting..."
		quit()


	# : BEGIN DIRECTORY TRAVERSAL : #
	# First we open the file to write to
	with open(_OUTPUT, 'wb') as outputFile:
		
		processes = os.listdir(_DIRECTORY)
		# The master logfile, we'll add all the others into this one
		logfile = []
		# Now traverse our proc directory
		for idx, process in enumerate(processes):
			# If the directory is a valid process directory
			if re.match(_VALIDPROCDIRS, process):
				# Create an empty list, each index will contain a line
				logentry = []
				# Now we'll open up this process directory, and then dump the contents
				# determined by the options, into the output log file
				try:
					thisprocesslist = os.listdir(_DIRECTORY + "/" + process)
				except OSError:
					print "Process no longer active: " + process + " skipping..."
					break
				# With our process directory listing, we'll then check what options we have,
				# and dump out the right details into the file
				header = "Log Entry for process id: " + str(process)
				logentry.append("\n")
				logentry.append("=" * len(header))
				logentry.append(header)
				logentry.append("=" * len(header))
				for jdx, opt in enumerate(thisprocesslist):
					# If we have the pgid option set, append the pgid number to the logfile
					if opt == "pgid" and _OPTIONS["pgid"]:
						logProcessOption(process, opt, logentry)
					
					# If we have the uid option set, append the uid number to the logfile
					if opt == "uid" and _OPTIONS["uid"]:
						logProcessOption(process, opt, logentry)
					
					# If we have the status option set, append the status logfile
					if opt == "status" and _OPTIONS["status"]:
						logProcessOption(process, opt, logentry)
					
					# If we have the maps option set, append the maps to the logfile
					if opt == "maps" and _OPTIONS["maps"]:
						logProcessOption(process, opt, logentry)

					# If we have the cwd option set, we'll get the path of the link and append it to the logfile
					if opt == "cwd" and _OPTIONS["cwd"]:
						logProcessLinkDestination(process, opt, logentry)
					
					# If we have the exe option set, we'll get the path of the link and append it to the logfile
					if opt == "exe" and _OPTIONS["exe"]:
						logProcessLinkDestination(process, opt, logentry)
					
					# If we have the root option set, we'll get the path of the link and append it to the logfile
					if opt == "root" and _OPTIONS["root"]:
						logProcessLinkDestination(process, opt, logentry)

				for logline in logentry:	
					logfile.append(logline)

		#: WRITE LOG TO FILE :#
		logstring = ""
		for line in logfile:
			logstring += line + _CR
		outputFile.write(logstring)

		#: CLOSE LOGFILE :#
		outputFile.close()
		print "Finished, logfile written to " + _OUTPUTDIR + "/" + _OUTPUT

def logProcessLinkDestination(process, opt, logentry):
	"""
	:	Some of the files in the process directories are links 
	:	here we will get their destinations and append them to
	:	the logfile.
	"""
	optheader = "Process " + opt + ": ";
	logentry.append(optheader)

	filename = _DIRECTORY + "/" + process + "/" + opt
	# If the file exists and is a link then we'll go aheand and append it to the log file
	if os.path.exists(filename) and os.access(filename, os.R_OK) and os.path.islink(filename):
		logentry.append(os.path.realpath(filename))

	else:
		logentry.append("Can't get link location")
	
	logentry.append("\n")



def logProcessOption(process, opt, logentry):
	"""
	:	This function will take in the process ID, the
	:	option name, and the logentry list. It will,
	:	check if the file can be opened and exists,
	:	then it populates an entry into the logentry list
	:
	"""
	# Set the header using the option name and append it
	optheader = "Process " + opt + ": ";
	logentry.append(optheader)

	filename = _DIRECTORY + "/" + process + "/" + opt
	# If our file exists and is readable
	if os.path.exists(filename) and os.access(filename, os.R_OK):
		try:
			# Try to open the file up
			filename = open(filename, 'r')
			lines = filename.readlines()
			for line in lines:
				# Append each line to the log entry list
				logentry.append(line)
			filename.close()
			# Append a small footer to the log file

		except IOError as err:
			# On error, append the message to the logfile
			logentry.append("Error Accessing File")
			logentry.append(str(err))
		except Exception, err:
			# On unknown error, append a message to the logfile
			logentry.append("Error")
			logentry.append(str(err))
	

if __name__ == "__main__":
	spamdrill();
