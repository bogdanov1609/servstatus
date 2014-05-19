import os, subprocess
import glob
import ConfigParser

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def runtest(script):
	process = subprocess.Popen(script, stdout=subprocess.PIPE)
	output = process.communicate()[0].strip()
	return output

#To add new test type one should write another Check_<TESTNAME> function\
def Check_ok(output, options):
	return output=="OK"

def Check_above(output, options):
	split = output.strip().split(" ")
	return int(split[0]) > int(options["threshold"])

def Check_below(output, options):
	split = output.strip().split(" ")
	return int(split[0]) < int(options["threshold"])


Config = ConfigParser.ConfigParser()
for file in glob.glob("/var/lib/check.d/*.cfg"):
	Config.read(file)
	for test in Config.sections():
		script = Config.get(test, "check")
		type = Config.get(test, "type").lower()
		if (script!=""):
			output = runtest(script)
			options = ConfigSectionMap(test)
			result = locals()["Check_"+type](output, options)
			if (result):
				print(test + ": " + bcolors.OKGREEN + output + bcolors.ENDC)
			else:
				print(test + ": " + bcolors.FAIL + output + bcolors.ENDC)
#ToDo: send emails?
