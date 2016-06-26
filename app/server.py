import cherrypy
import isbnlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import GOOGLE_OAUTH, ISBNDB_KEY, GOOGLE_SPREADSHEET
from trove import Trove

isbnlib.config.add_apikey('isbndb', ISBNDB_KEY)

class LibraryCatalogue(object):

	def __init__(self):
		scope = ['https://spreadsheets.google.com/feeds']
		credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_OAUTH, scope)
		self.gc = gspread.authorize(credentials)
		self.link = GOOGLE_SPREADSHEET
		self.trove = Trove()


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
		
		#should check if has been collected before

		canonical = None;
		#first check trove
		canonical = self.trove.extract(clean_isbn);
		if not canonical :
			# try alternative isbn form
			print "trying alternative form "
			alt_isbn = clean_isbn;
			if isbnlib.is_isbn13(clean_isbn):
				alt_isbn = isbnlib.to_isbn10(clean_isbn)
			else :
				alt_isbn = isbnlib.to_isbn13(clean_isbn)
			canonical = self.trove.extract(alt_isbn);
			if canonical :
				clean_isbn = alt_isbn
		if not canonical :
			canonical = self.__reduce_metadata(clean_isbn,['merge','isbndb','openl'])
			if not canonical:
				return "no metadata found for isbn: " + clean_isbn
			canonical['source']='isbnlib'
			canonical["Authors"] = u', '.join(canonical["Authors"])
			canonical['link']=None

		row_data = ['isbn:'+clean_isbn, canonical["Title"], canonical["Authors"], canonical["Year"], canonical["Publisher"],canonical['link']]
		return self.__add_and_render(row_data)

	@cherrypy.expose
	def trovelink(self):
		return """<html>
			<head></head>
			<body>
				<form method="get" action="/trover" name="trovelinkform">
					<label for="trovelink">Trovelink: </label><input type="text" value="" name="trovelink"/>
					<button type="submit">Add</button>
				</form>
			</body>
		</html>"""

	@cherrypy.expose
	def trover(self,trovelink) :
		data = self.trove.extract_from_link(trovelink);
		row_data = [None, data["Title"], data["Authors"], data["Year"], data["Publisher"],data['link']]
		return self.__add_and_render(row_data)

	def __add_and_render (self,row_data) :
		wks = self.gc.open_by_url(self.link).sheet1
		wks.append_row(row_data);
		row_data.append(self.link);
		return u"""<html>
			<head></head>
			<body>
				<h1>SUCCESS, but is this right?</h1>
				<table border='0'>
				<tr><td><strong>isbn:</strong> </td><td>{}</td></tr>
				<tr><td><strong>title:</strong> </td><td>{}</td></tr>
				<tr><td><strong>author:</strong> </td><td>{}</td></tr>
				<tr><td><strong>year:</strong> </td><td>{}</td></tr>
				<tr><td><strong>publisher:</strong> </td><td>{}</td></tr>
				<tr><td><strong>trove-link:</strong> </td><td>{}</td></tr>
				</table>
				<p>If not remove it from the google spreadsheet <a href='{}' target='_blank'>here</a></p>
			</body>
			<html>""".format(*row_data)

	def __reduce_metadata(self,isbn,services) :
		canonical = self.__collect_metadata(isbn,services[0], None);
		for service in services[1:]:
			canonical = self.__collect_metadata( isbn, service, canonical)
		return canonical;

	def __collect_metadata(self,isbn,service, canonical) :
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

if __name__ == '__main__':
	cherrypy.quickstart(LibraryCatalogue())