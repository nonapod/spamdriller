spamdriller
===========

A little process drilling script written in Python!

Idea
====
After getting given an old Cent 4 box at work due to a large influx of spam, I decided, 
if I was able to maybe explore the process of all of the files firing off for mail,
mainly QMail, then maybe I would be able to find the root script of it all. Sadly
these proc files disappear as quickly as they appear, so you can't explore them, this
is where the idea for this little tool came from.

This script will allow you to take a snapshot of a proc directory and spit out a log file
for you to read. It will traverse the proc directory and dump whatever options you provide
it. I would like to add better formatting and more functionality over time.

This might also server useful as a script for general process exploration, as over time, if
need be, I may add more options.

How To
======
This was tested on Python 2.7, I haven't tested it on any other version so you may need to
modify it if it doesn't work on earlier versions.

-d specify alternate directory, default is /proc
-r dump root application location
-s dump process status
-u dump uid
-m dump maps
-a dump all options
-p show default options
-l directory to output the logfile, default is current directory
   the filename format is spamhk_(timestamp goes here here).log
-w if you're using cygwin and want this to display in Windows
   then this option will use \r\n for carriage return instead of \n
   NOTE: This does autodetect, but for Cygwin you will need this option.
-h show this help again

