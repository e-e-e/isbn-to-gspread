from ConfigParser import SafeConfigParser
import os

config = SafeConfigParser({
	'port':8080,
	'google_credentials':'credentials.json',
	'images_dir':'images',
	'css_dir':'css'
	})

config.read('config.ini')

GOOGLE_SPREADSHEET = config.get('authentication','google_speadsheet')

GOOGLE_OAUTH = config.get('authentication', 'google_credentials')
ISBNDB_KEY = config.get('authentication','isbndb_key')
TROVE_KEY = config.get('authentication','trove_key')


SERVER_PORT = config.get('server', 'server_port')
SERVER_IMAGES = config.get('server', 'images_dir')
SERVER_CSS = config.get('server', 'css_dir')