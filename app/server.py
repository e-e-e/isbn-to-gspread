import cherrypy
import isbnlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_OAUTH, ISBNDB_KEY, GOOGLE_SPREADSHEET

isbnlib.config.add_apikey('isbndb', ISBNDB_KEY)

def reduce_metadata(isbn,services) :
	canonical = collect_metadata(isbn,services[0], None);
	for service in services[1:]:
		canonical = collect_metadata( isbn, service, canonical)
	return canonical;

def collect_metadata(isbn,service, canonical) :
	try :
		record = isbnlib.meta(isbn, service=service)
		if canonical :
			for key in canonical :
				if not canonical[key] and record[key]:
					canonical[key] = record[key]
		else :
			return record
	except :
		pass
	return canonical

class LibraryCatalogue(object):

	def __init__(self):
		scope = ['https://spreadsheets.google.com/feeds']
		credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_OAUTH, scope)
		self.gc = gspread.authorize(credentials)
		self.link = GOOGLE_SPREADSHEET


	@cherrypy.expose
	def index(self):
		return """<html>
			<head></head>
			<body>
				<form method="get" action="/isbn" name="isbnform">
					<label for="isbn">ISBN: </label><input type="text" value="" name="isbn" maxlength="20"/>
					<button type="submit">Add</button>
				</form>
			</body>
		</html>"""
	
	@cherrypy.expose
	def isbn(self,isbn):
		#adds isbn to google spread sheet
		#check if valid
		clean_isbn = isbnlib.clean(isbn)
		if isbnlib.notisbn(clean_isbn):
			return "not valid isbn"
		wks = self.gc.open_by_url(self.link).sheet1
		#should check if has been collected before
		canonical = reduce_metadata(clean_isbn,['merge','isbndb','openl'])
		if not canonical:
			return "no metadata found for isbn: " + clean_isbn
		row_data = [clean_isbn, canonical["Title"], ', '.join(canonical["Authors"]), canonical["Year"], canonical["Publisher"]]
		wks.append_row(row_data);
		row_data.append(self.link);
		return """<html>
			<head></head>
			<body>
				<p><strong>success</strong>, but is this right?</p>
				<p><strong>isbn:</strong> {}</p>
				<p><strong>title:</strong> {}</p>
				<p><strong>author:</strong> {}</p>
				<p><strong>year:</strong> {}</p>
				<p><strong>publisher:</strong> {}</p>
				<p>If not remove it from the google spreadsheet <a href='{}' target='_blank'>here</a></p>
			</body>
			<html>""".format(*row_data)

if __name__ == '__main__':
	cherrypy.quickstart(LibraryCatalogue())