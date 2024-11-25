python grepallin.py 20*.pdf | sed -e "/^On /p;d" > out
type 20031001-on.dat >> out
type 20060401-mar-90.dat >> out
type 20110101-mar-116.dat >> out
type 20130101-jun-130.dat >> out
type in_progress.dat >> out

