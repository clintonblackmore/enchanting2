"""Here we run a web server to serve static files and web socket server"""

import os.path
import mimetypes

from collections import OrderedDict

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource


class ClientConnection(WebSocketApplication):
    event_loop = None

    def on_open(self):
        ClientConnection.event_loop.client_connected(self)

    def on_message(self, message):
        ClientConnection.event_loop.message_from_client(message, self)

    def on_close(self):
        ClientConnection.event_loop.client_disconnected(self)


def static_file_server(environ, start_response):
    filename = "web" + environ["PATH_INFO"]
    mime = "text/html"
    status = "200 OK"
    content = None

    if os.path.isdir(filename):
        # We need to create a directory listing
        # One line per file
        crawl_dir = filename  # local directory we are looking at
        # relative URL of directory
        http_dir = environ["PATH_INFO"].lstrip("/")

        # special case -- if we are looking at the root directory,
        # return the snap web page
        if http_dir == "":
            filename = "web/snap.html"
        else:
            # If the directory doesn't end in a "/", we have to issue a
            # redirect
            if not http_dir.endswith("/"):
                start_response(
                    '301 Redirect', [('Location', '/' + http_dir + '/'), ])
                return "301 Moved Permanently"
            content = "<html><head></head><body>" \
                      "<h1>Listing of %s</h1><pre>" % http_dir
            filelist = os.listdir(crawl_dir)
            hreflist = ['<a href="%s">%s</a>' % (f, f) for f in filelist]
            content += "\n".join(hreflist)
            content += "</pre></body></html>"

    if os.path.isfile(filename):
        mime = mimetypes.guess_type(filename)
        if filename.endswith(".js"):
            mime = "application/javascript"
        content = open(filename).readlines()

    if content is None:
        status = "404 Not Found"
        content = "<h1>404 Not found</h1><p>%s does not exist" % (filename)

    start_response(status, [("Content-Type", mime)])
    return content


def run_web_servers(port):
    resource = Resource(
        OrderedDict([
            ('/ws', ClientConnection),
            ('.*', static_file_server)
        ])
    )

    server = WebSocketServer(("", port), resource, debug=False)
    print "Now listening on port %d" % port
    server.serve_forever()
