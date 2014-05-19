import os, subprocess
import glob

def runtest(test, script):
	process = subprocess.Popen(script, stdout=subprocess.PIPE)
	output = process.communicate()[0].strip()
	if (output != "OK"):
		print("Test "+test+" failed ("+script+"):" + output)

for test in glob.glob("/var/lib/check.d/*.cfg"):
	f = open(test, "r")
	testname = "global"
	for line in f:
		line=line.strip()
		if (len(line)==0):
			continue
		if (line[0]=='['):
			testname = line
		else:
			runtest(testname, line)

