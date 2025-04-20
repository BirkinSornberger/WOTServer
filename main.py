import os
import http.server
import socketserver
import time
import gzip
import io
import threading
from urllib.parse import urlparse, parse_qs

PORT_HTTP = 80
PORT_HTTP_ALT = 443  # Port 443 serves HTTP

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class ServeHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'  # Use HTTP/1.1

    def send_response(self, code, message=None):
        """Override to prevent default Date and Server headers."""
        print(f"send_response called with code: {code}")
        self.log_request(code)
        self.send_response_only(code, message)

    def end_headers(self):
        """Override to finalize headers without adding defaults."""
        super().end_headers()
    

    def do_POST(self):
        # Get the client IP address
        client_ip = self.client_address[0]
        print(f"Client IP: {client_ip}")

        # Parse query parameters
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        print(f"Query Params: {query_params}")

        # Read and log the body of the request
        content_length = self.headers.get('Content-Length')
        if content_length:
            content_length = int(content_length)
            post_data = self.rfile.read(content_length)
            print(f"Body: {post_data.decode('utf-8')}")
        else:
            print("No Content-Length header provided.")

        # Create & log a response based on the request path
        response, content_type = self.create_response(parsed_path.path)
        print(f"Response: {response}")

        # Spoof headers for /tapservice/api endpoint
        if parsed_path.path == "/tapservice/api/":
            self.send_response(200)  # 200 OK

            # Gzip the response body
            gzipped_response = io.BytesIO()
            with gzip.GzipFile(fileobj=gzipped_response, mode="wb") as gz:
                gz.write(response.encode('utf-8'))
            gzipped_response = gzipped_response.getvalue()

            # This may be unnecessary, testing if the client verifies the headers in any way
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, proxy-revalidate, max-age=0")
            self.send_header("Connection", "keep-alive")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(gzipped_response)))
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Date", self.date_time_string())  # Use dynamic date
            self.send_header("Referrer-Policy", "same-origin")
            self.send_header("Server", "nginx/1.24.0 (Ubuntu)")
            self.send_header("Strict-Transport-Security", "max-age=3600")
            self.send_header("Vary", "Origin, Accept-Encoding")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("X-TC-Digest", "4f2564d324730e58cdedcb55a06a240d")
            self.end_headers()

            self.wfile.write(gzipped_response)

            print("Response sent")
            print("\n" * 2)
            print(f"Handling request for path: {parsed_path.path}")
            return  # Prevent further execution for /tapservice/api

        # Sending default headers for other endpoints for now
        self.send_response(202)  # 202 Accepted
        self.send_header("Date", self.date_time_string())
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

        print("Response sent")
        print("\n" * 4)
        print(f"Handling request for path: {parsed_path.path}")

    def create_response(self, path):
        # Normalize the path to avoid trailing slash issues
        path = path.rstrip('/')

        if path == "/tapservice/api":
            return self.get_json_response('saltResponse.json'), "application/json; charset=UTF-8"
        elif path == "/process_queue.php":
            return "The request has been accepted for processing, but the processing has not been completed.", "text/plain; charset=UTF-8" 
        elif path == "/get_server.php":
            return "Server info response", "text/plain; charset=UTF-8"  # Remove this
        else:
            return '{"error": "Unknown endpoint"}', "application/json; charset=UTF-8"

    def get_json_response(self, filename):
        """Reads a JSON file from the current working directory and returns its content."""
        try:
            # Construct the full path to the file in the current working directory
            file_path = os.path.join(os.getcwd(), filename)
            # Open and read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File {filename} not found in {os.getcwd()}.")
            return '{"error": "File not found"}'
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return '{"error": "An error occurred while reading the file"}'


def run_http_server(port):
    with socketserver.TCPServer(("", port), ServeHandler) as httpd:
        print(f"Serving HTTP on port {port}")
        httpd.serve_forever()


# Probably won't use threading long term
threading.Thread(target=run_http_server, args=(PORT_HTTP,)).start()
#threading.Thread(target=run_http_server, args=(PORT_HTTP_ALT,)).start()