import sys
import subprocess
import re
import datetime

# print(sys.argv)

def scrape_stmt(stmt_name) :

	targ=sys.argv[2]

	app = subprocess.Popen(['c:/gener/poppler-0.68.0/bin/pdftohtml','-i', 
													'-stdout', stmt_name], stdout=subprocess.PIPE, 
												 universal_newlines=True)
	for lin in app.stdout :
		mo = re.search(targ,lin)
		if mo :
			print('Found '+ stmt_name + ':' + lin)

line= None

diry = subprocess.Popen(['ll', '-0', '-/', sys.argv[1]],
											  stdout=subprocess.PIPE, 
											  universal_newlines=True)
for line in diry.stdout :
	print('Do '+line.rstrip())
	cc = scrape_stmt(line.rstrip())

