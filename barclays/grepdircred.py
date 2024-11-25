import sys
import subprocess
import re
import datetime

# print(sys.argv)

mode=' '
iter=0
citer=0
datestr= ' '
date=None
amount_str = None
ref_str = None
from_str = None
datestr = None

app = subprocess.Popen(['c:/gener/poppler-0.68.0/bin/pdftohtml','-i', '-stdout', sys.argv[1]], stdout=subprocess.PIPE, universal_newlines=True)
for line in app.stdout :
	mo = re.search('([0-9][0-9]?) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)<br', line)
	if mo :
		print('Found date '+line)
#		print('Start ' + str(mo.start()) +' End '+  str(mo.end()))
#		print('Day '+ line[0:2])
		day = int(line[0:mo.end()-7])
		mon = line[mo.end()-6:mo.end()-3]
		print('Day '+ line[0:mo.end()-7])
		print('month '+mon)
		this_year = d_obj.year
		try:
			tr_dt = datetime.datetime.strptime(line[0:mo.end()-3]+' '+str(d_obj.year), '%d %b %Y')
		except ValueError:
			this_year = d_obj.year - 1
			tr_dt = None
		if tr_dt == None or tr_dt > d_obj : 
			print('In future')
			tr_dt = datetime.datetime.strptime(line[0:mo.end()-3]+' '+str(this_year), '%d %b %Y')
		print('Tr Date '+tr_dt.strftime('%Y %m %d'))
			

	if re.search('Your Community Account', line) :
		mode = 'D'
		iter = 1

	if mode == 'D' and iter == 0 :
		datestr=line[11:22]
		format_str='%d %b %Y'
		d_obj = datetime.datetime.strptime(datestr, format_str)
#		print ('Date is '+datestr)
#		print (d_obj.date())
#		print(d_obj.year)

	if re.search('^Direct credit from',line) :
		citer = 6
		amount_str = None
		ref_str = None
		fro = re.search('<br/>',line[18:])
		e = fro.start() + 18 if fro != None else len(line) -1
		from_str = re.sub('&#160;','',re.sub('&amp;','&',line[18:e]))
		print('From '+ from_str)
		print(line[18:e])
		fro = re.search(';Ref:(.*)<br/>',line)
		if fro :
			print('R '+fro.group(1))
			ref_str = re.sub('<br/>','',fro.group(1))
			from_str = re.sub('Ref:.*','',from_str)

	if citer > 0 and amount_str == None and re.search(r'[0-9]+[.][0-9][0-9]',line) :
		print('Line '+line)
		amount_str = re.sub('<br/>','',line).rstrip()
		print('Amount '+ amount_str)

	mor = re.search('^Ref:.*<br/>',line)

	if citer == 5 and mor :
		ref_str = line[4:mor.end()-5]
		print('Ref '+ref_str)

	if citer > 0 and mor :
		ref_str = line[4:mor.end()-5]
		print('Ref '+ref_str)

	if amount_str != None and ref_str != None :
		print('On ' + tr_dt.strftime('%Y %m %d') + ' ' + amount_str + 
					' Ref ' + ref_str + 
					' From ' + from_str )
		citer = 0
		amount_str = None
		ref_str = None	

	iter = iter - 1
	citer = citer - 1
