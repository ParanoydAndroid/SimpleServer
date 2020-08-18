from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler

import json
import cgi
import threading

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
        
        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message).encode())
        
def j_run(server_class=HTTPServer, handler_class=JSONServer):
    server_address = ('', 49081)
    httpd = server_class(server_address, handler_class)
    
    print('Starting JSON server on port 49081')
    httpd.serve_forever()


def h_run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 49080)
    httpd = server_class(server_address, handler_class)
    print('Starting HTTP server on port 49080')
    httpd.serve_forever()


if __name__ == '__main__':
    main()
