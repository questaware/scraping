import sys
import subprocess
import re
import datetime

# print(sys.argv)

def scrape_stmt(stmt_name) :

	mode=' '
	iter=0
	citer=0
	datestr= ' '
	date=None
	amount_str = None
	ref_str = None
	from_str = None
	datestr = None

	format_str='%Y%m%d'
	d_obj = datetime.datetime.strptime(stmt_name[0:4]+'1231', format_str)
	print(d_obj)

	app = subprocess.Popen(['c:/gener/poppler-0.68.0/bin/pdftohtml','-i', 
													'-stdout', stmt_name], stdout=subprocess.PIPE, 
												 universal_newlines=True)
	for lin in app.stdout :
		line = re.sub('&#160;','~',re.sub('&amp;','&',lin))
		mo = re.search('^([0-9]+) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)<br',
									 line)
		if mo == None :
			mo = re.search('^([0-9]+) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[&~]',
										 line)
		if mo :
			print('Found date '+line)
			try:
				day = int(mo.group(1))
				mon = mo.group(2)
				print('Day '+ line[0:mo.end()-7])
				print('month '+mon)
				this_year = d_obj.year
				tr_dt = datetime.datetime.strptime(str(this_year)+mon+str(day), '%Y%b%d')
			except ValueError:
				this_year = d_obj.year - 1
				tr_dt = None
			if tr_dt == None or tr_dt > d_obj : 
				print('In future '+ day +' '+ mon +' '+ str(this_year))
				tr_dt = datetime.datetime.strptime(str(this_year-1)+mon+str(day),'%Y%b%d')
			print('Tr Date '+tr_dt.strftime('%Y %m %d'))
				

		sd = re.search('^<b>Statement for [0-9]+ [A-Z][a-z][a-z] ([0-9]+ [A-Z][a-z][a-z] 20[0-9][0-9])', line)
		if sd :
			print(sd.group())
			datestr=line[26:36]
			format_str='%d %b %Y'
			d_obj = datetime.datetime.strptime(datestr, format_str)

		if re.search('Your Community Account', line) :
			mode = 'D'
			iter = 2

		if mode == 'D' and iter >= 0 :
			d_mo = re.search('[0-9]+ [A-Z][a-z][a-z] 2[0-9][0-9][0-9]',line[2:])
			if d_mo :
				mode = ' '
				datestr = line[2+d_mo.start():2+d_mo.end()]
				print('Dsource '+line)
				print('SDate '+datestr)
				format_str='%d %b %Y'
				d_obj = datetime.datetime.strptime(datestr, format_str)
		#		print ('Date is '+datestr)
		#		print (d_obj.date())
		#		print(d_obj.year)

		dc_mo = re.search('^(DIRECT CREDIT|INTERNET BANKING TRANSFER|TRANSFER|STANDING ORDER) FROM([ <])',line.upper())

		if dc_mo == None :
			dc_mo = re.search('~(DIRECT CREDIT|INTERNET BANKING TRANSFER|TRANSFER|STANDING ORDER) FROM([ <])',line.upper())

		if dc_mo and ( len(line) < dc_mo.end()+7 or
									 line[dc_mo.end():dc_mo.end()+7].lower() != 'account' ) :
			mode = 'A'
			citer = 6
			amount_str = None
			ref_str = None
			beg = dc_mo.end(1)
			fro = re.search('<br/>',line[beg:])
			e = fro.start() + beg if fro != None else len(line) -1
			from_str = line[beg+6:e]
			rf_mo = re.search('<i>',from_str)
			if rf_mo :
				from_str = from_str[0:rf_mo.start()]
			rf_mo = re.search('Ref:',from_str)
			if rf_mo :
				from_str = from_str[0:rf_mo.start()]
			from_str = from_str.lstrip()
			print('From '+ from_str)

			tgt = re.sub('~','', from_str.upper())
			if tgt in alias_dict :
				ref_str = 'Deena ' + str(alias_dict[tgt])
				print('DefRef '+ref_str)
			else:
				print('TryRef '+(ref_str if ref_str != None else '<None>'))
				fro = re.search(';*Ref:(.*)<br/>',line)
				if fro :
					print('R '+fro.group(1))
					ref_str = re.sub('<br/>','',fro.group(1))
					from_str = re.sub('Ref:.*','',from_str)

			if dc_mo.group(2) == '<' :
				print('Got '+ from_str)
				from_str = None

		if citer > 0 and from_str == None :
			print('?'+line)
			dc_mo = re.search(r'[Aa]ccount ([^<]*)(<br/>)', line)
			if dc_mo :
				print('try '+ dc_mo.group(1))
				if dc_mo.group(1).upper() in alias_dict :
					ref_str = 'Deena ' + str(alias_dict[dc_mo.group(1).upper()])
					from_str = dc_mo.group(1)
				else :
					if re.search('90330957 at 20-37-16', line) == None :
						print('Lost '+dc_mo.group(1))

		if citer > 0 and amount_str == None :
			am_mo = re.search(r'^ *([0-9,]+[.][0-9][0-9])',line)
			if am_mo == None :
				am_mo = re.search(r'~ *([0-9,]+[.][0-9][0-9])',line)

			if am_mo :
				print('Line '+line)
				amount_str = am_mo.group(1).rstrip()
				amount_str = re.sub(',','',amount_str)
				print('Amount '+ amount_str)

		ref_stt = 3 if line[0:3] == '<i>' else 0
		mor = re.search('^Ref:.*<br/>',line[ref_stt:])

		if citer == 5 and ref_str == None and mor :
			ref_str = line[ref_stt+4:ref_stt+mor.end()-5]
			print('Ref '+ref_str)

		if citer > 0 and ref_str == None and mor :
			ref_str = line[ref_stt+4:ref_stt+mor.end()-5]
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

	return 0

print('Pat '+ sys.argv[1])

alias_dict = {}

fd = open('data/aliases.dat','r')
if fd :
	for line in fd :
		if len(line) < 6 : continue
		alias_dict[line[4:].rstrip().upper()] = int(line[0:2])
		print('Dict '+line[4:].rstrip())
	fd.close()

line= None

diry = subprocess.Popen(['ll', '-0', '-/', sys.argv[1]],
											  stdout=subprocess.PIPE, 
											  universal_newlines=True)
for line in diry.stdout :
	print('Do '+line.rstrip())
	cc = scrape_stmt(line.rstrip())
