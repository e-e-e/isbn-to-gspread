import urllib
import urlparse
import requests
import isbnlib
from config import TROVE_KEY

import pprint
pp = pprint.PrettyPrinter(indent=1)

class Trove(object):

	"""Simple interface for Trove"""
	
	def __init__(self, key=TROVE_KEY):
		super(Trove, self).__init__()
		self.key = key;

	def extract(self,isbn) :
		books = self.find_isbn(isbn)
		if books : 
			v = self.get_metadata(books[0], isbn)
			if v :
				link = books[0]['troveUrl']+'?q&versionId='+urllib.quote(v['id'])
				return self.massage_data(v,link)
		return None

	def massage_data(self, v, link) :
		r = v['record']
		if type(r) is list:
			r = r[0]
		print r;
		authors = r.get('creator','');
		if type(authors) is list and len(authors) > 0:
			authors = u' | '.join([unicode(o) for o in authors])
		return {
			'Authors' : authors,
			'Title' : r.get('title',''),
			'Year' : r.get('issued',''),
			'Publisher': r.get('publisher',''),
			'source': r.get('metadataSource',''),
			'link' : link
		};

	def find_isbn (self, isbn) :
		res = requests.get('http://api.trove.nla.gov.au/result?q=isbn:{}&zone=book&encoding=json&key={}'.format(isbn,self.key))
		records = res.json()['response']['zone'][0]['records']
		if int(records['total']) > 0 :
			return records['work']
		return None

	def get_metadata(self, work, isbn):
		res = requests.get('http://api.trove.nla.gov.au{}?encoding=json&reclevel=full&include=workversions&key={}'.format(work['url'],self.key))
		versions = res.json()['work']['version']
		#pp.pprint(res.json());
		for version in versions :
			record = version['record'];
			if type(record) is list:
				#get first matching record
				for v in record:
					if self.version_with_isbn(v,isbn) :
						return version;
			elif self.version_with_isbn(record,isbn) :
				return version;
		return None

	def version_with_isbn(self, record, isbn) :
		ids = record.get('identifier',[])
		gen = (x for x in ids if isinstance(x,dict))
		for obj in gen:
			i_type = obj.get('type');
			i_value = obj.get('value');
			if i_type and i_type.startswith('isbn') and isbnlib.get_canonical_isbn(i_value) == isbn :
				return True
		return False

	def extract_from_link(self, link) :
		url = urlparse.urlparse(link);
		res = requests.get('http://api.trove.nla.gov.au{}?{}&encoding=json&reclevel=full&include=workVersions&key={}'.format(url.path,url.query,self.key))
		queries = urlparse.parse_qs(url.query);
		vid = queries.get('versionId')
		work = res.json()['work']
		versions = work['version']
		newlink = work.get['troveUrl'];
		for v in versions :
			if v['id'] == vid[0] :
				newlink = newlink +'?q&versionId='+urllib.quote(v['id'])
				return self.massage_data(v, newlink+'&versionId')
		newlink = newlink +'?q&versionId='+urllib.quote(v['id'])
		return self.massage_data(versions[0], link)



if __name__ == '__main__':
	#646324853
	#9780241956182
	isbn = isbnlib.canonical('9781584350118');
	trove = Trove();
	books = trove.find_isbn(isbn)
	v = trove.get_metadata(books[0], isbn)
	#print books[0]['troveUrl']+'?q&versionId='+v['id'];

	pp.pprint(v)