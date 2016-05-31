from app.server import LibraryCatalogue
from app.config import SERVER_PORT
import cherrypy

def application(environ, start_response):
	cherrypy.config.update({
		'server.socket_port': SERVER_PORT
	})
	app = cherrypy.tree.mount(LibraryCatalogue(), '/')
	return cherrypy.tree(environ, start_response)