import sys
import os
import subprocess
import glob
import ConfigParser
import datetime
import shlex
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class TextColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def ConfigSectionDict(Config, section):
    optionDict = {}
    optionNames = Config.options(section)
    for option in optionNames:
        try:
            optionDict[option] = Config.get(section, option)
            if optionDict[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            optionDict[option] = None
    return optionDict

#Runs specific script and returns output
def RunScript(script):
	args = shlex.split(script)
	process = subprocess.Popen(args, stdout=subprocess.PIPE)
	output = process.communicate()[0].strip()
	return output

#To add new test type one should write another Check_<TESTNAME> function
def Check_ok(output, options):
	return output=="OK"

def Check_above(output, options):
	split = output.strip().split(" ")
	try:
		return int(split[0]) > int(options["threshold"])
	except:
		return false

def Check_below(output, options):
	split = output.strip().split(" ")
	try:
		return int(split[0]) < int(options["threshold"])
	except:
		return false

#Sends email
def SendEmail(server, port, login, password, source, receivers, text, html):
	smtp = SMTP()
	smtp.connect(server, port)
	smtp.login(login, password)
	from_addr = "<%s>" % source
	for target in receivers:
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "Server errors"
		msg['From'] = from_addr
		msg['To'] = target.strip()
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(html, 'html')
		msg.attach(part1)
		msg.attach(part2)
		date = datetime.datetime.now().strftime( "%d/%m/%Y %H:%M" )
		smtp.sendmail(source, target.strip(), msg.as_string())
	smtp.quit()

#Executes specific config file and appends failed tests reports into errorList
def ExecuteConfigFile(configFile, errorList):
	Config = ConfigParser.ConfigParser()
	Config.read(configFile)
	for test in Config.sections():
		script = Config.get(test, "check")
		type = Config.get(test, "type").lower()
		if (script!=""):
			try:
				output = RunScript(script)
				options = ConfigSectionDict(Config, test)
				result = globals()["Check_"+type](output, options)
				if (result):
					print(test + ": " + TextColors.OKGREEN + output + TextColors.ENDC)
				else:
					print(test + ": " + TextColors.FAIL + output + TextColors.ENDC)
					errorList.append({"test" : test, "output" : output, "script" : script})
			except:
				print "Error executing script " + script + " : " + str(sys.exc_info()[1]) + str(sys.exc_info()[2])

#Executes scripts in /var/lib/check.d/
def ExecuteConfigs(configPattern):
	errList = []
	for file in glob.glob(configPattern):
		print(file)
		ExecuteConfigFile(file, errList)
	return errList

#Transforms failed tests array into
def FormatReport(report):
	plaintext = "Failed tests: "
	htmltext = "Failed tests: "
	for r in report:
		plaintext = "%s\n%s(%s) : %s" % (plaintext, r["test"], r["script"], r["output"])
		htmltext = "%s<BR /><B>%s</b>(%s) : <FONT color=red> %s </font>" % (htmltext, r["test"], r["script"], r["output"])
	return (plaintext, htmltext)

#Main function
def main():
	report = ExecuteConfigs("/var/lib/check.d/*.cfg")
	if (len(report)>0):
		print(TextColors.OKBLUE + "Sending e-mail..." + TextColors.ENDC)
		Config = ConfigParser.ConfigParser()		
		Config.read("emails.cfg")

		(plaintext, htmltext) = FormatReport(reports)

		SendEmail(Config.get("main", "server"),
			Config.get("main", "port"),
			Config.get("main", "login"),
			Config.get("main", "password"),
			Config.get("main", "source"),
			Config.get("main", "target").split(","),
			plaintext, htmltext)
		print(bcolors.OKBLUE + "done" + bcolors.ENDC)

if  __name__ ==  "__main__" :    
	main()
