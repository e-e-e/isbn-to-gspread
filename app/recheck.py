import isbnlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_OAUTH, ISBNDB_KEY, GOOGLE_SPREADSHEET
from trove import Trove

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_OAUTH, scope)
gc = gspread.authorize(credentials)
link = GOOGLE_SPREADSHEET
trove = Trove()
wks = gc.open_by_url(link).sheet1

for i in xrange(631,1000) :
	row = wks.row_values(i);
	if row[5] == 'None':
		isbn = row[0][5:]
		old_isbn = isbn;
		print 'getting ', isbn

		if isbnlib.is_isbn13(isbn):
			isbn = isbnlib.to_isbn10(isbn)
		else : 
			isbn = isbnlib.to_isbn13(isbn)
		canonical = trove.extract(isbn)
		if not canonical:
			canonical = trove.extract(old_isbn)
		if canonical :
			print '---------------------------'
			print 'Replacing', i, 'row'
			#print row
			row_data = ['isbn:'+isbn, canonical["Title"], canonical["Authors"], canonical["Year"], canonical["Publisher"],canonical['link']]
			#print row_data
			print "updating "
			for j in range(0,len(row_data)):
				print '-cell',i,j,':'
				print '\tfrom:', row[j]
				print '\tto:', row_data[j]
				wks.update_cell(i,j+1,row_data[j])
