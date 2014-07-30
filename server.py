"""Here we run a web server to serve static files and web socket server"""

import os.path
import mimetypes

from geventwebsocket.server import WebSocketServer
from geventwebsocket.resource import Resource, WebSocketApplication
from geventwebsocket.protocols.wamp import WampProtocol, export_rpc

def static_file_server(environ, start_response):
	filename = "web" + environ["PATH_INFO"]
	mime = "text/html"
	if os.path.isfile(filename):
		status = "200 OK"
		mime = mimetypes.guess_type(filename)
		content = open(filename).readlines()
	else:
		status = "404 Not Found"
		content = "<h1>404 Not found</h1><p>%s does not exist" % (filename)

	start_response(status, [("Content-Type", mime)])
	return content
	
def run_web_servers(port):
    resource = Resource({
     #   '^/wamp_example$': WampApplication,
        r'.*': static_file_server
    })

    server = WebSocketServer(("", port), resource, debug=True)
    print "Now listening on port %d" % port
    server.serve_forever()
    
