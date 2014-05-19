import os, subprocess

for script in os.listdir("./tests/"):
	process = subprocess.Popen("./tests/"+script, stdout=subprocess.PIPE)
	output = process.communicate()[0].strip()
	if (output != "OK"):
		print(script+" failed:")
		print(output)
