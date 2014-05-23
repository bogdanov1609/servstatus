#!/usr/bin/python
# -*- coding: utf-8 -*-

import os 
import subprocess
import glob
import ConfigParser
import smtplib
import datetime
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

#To add new test type one should write another Check_<TESTNAME> function
def Check_ok(output, options):
	return output=="OK"

def Check_above(output, options):
	split = output.strip().split(" ")
	return int(split[0]) > int(options["threshold"])

def Check_below(output, options):
	split = output.strip().split(" ")
	return int(split[0]) < int(options["threshold"])

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

Config = ConfigParser.ConfigParser()
report = []

#Executing scripts
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
				report.append({"test" : test, "output" : output, "script" : script})

#If we have something to tell about
if (len(report)>0):
	print(bcolors.OKBLUE + "Sending e-mail..." + bcolors.ENDC)
	Config.read("emails.cfg")
	plaintext = "Failed tests: "
	htmltext = "Failed tests: "
	for r in report:
		plaintext = "%s\n%s(%s) : %s" % (plaintext, r["test"], r["script"], r["output"])
		htmltext = "%s<BR /><B>%s</b>(%s) : <FONT color=red> %s </font>" % (htmltext, r["test"], r["script"], r["output"])
	SendEmail(	Config.get("main", "server"),
			Config.get("main", "port"),
			Config.get("main", "login"),
			Config.get("main", "password"),
			Config.get("main", "source"),
			Config.get("main", "target").split(","),
			plaintext, htmltext)
	print(bcolors.OKBLUE + "done" + bcolors.ENDC)
