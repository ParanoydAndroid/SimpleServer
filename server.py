from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler

import json
import cgi
import os
import threading
import urllib
from http import HTTPStatus

def main():
    h_server = threading.Thread(target=h_run)
    j_server = threading.Thread(target=j_run)

    j_server.start()
    h_server.start()


class JSONServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    def do_GET(self):
        data = None
        with open('json.txt') as f:
            data = json.load(f)

        self._set_headers()
        self.wfile.write(json.dumps(data).encode())
        

    def do_POST(self):
        ctype, _ = cgi.parse_header(self.headers.get_content_type())
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        length = int(self.headers.get_param('content-length')) # type: ignore
        message = json.loads(self.rfile.read(length))
        
        message['received'] = 'ok'
        
        self._set_headers()
        self.wfile.write(json.dumps(message).encode())
        
class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                                parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/html")
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return f
        except:
            f.close()
            raise

def j_run(server_class=HTTPServer, handler_class=JSONServer):
    server_address = ('', 49081)
    httpd = server_class(server_address, handler_class)
    
    print('Starting JSON server on port 49081')
    httpd.serve_forever()


def h_run(server_class=HTTPServer, handler_class=CORSHTTPRequestHandler):
    server_address = ('', 49080)
    httpd = server_class(server_address, handler_class)
    print('Starting HTTP server on port 49080')
    httpd.serve_forever()


if __name__ == '__main__':
    main()
