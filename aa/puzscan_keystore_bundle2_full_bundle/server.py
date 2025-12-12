#!/usr/bin/env python3
"""
Minimal HTTPS static server using bundled PEM cert/key.
Usage: ./start.sh [PORT]
Default port: 4443
Serves files from the current directory.
Security note: This is for testing/demo only. Do not expose to untrusted networks.
"""
import http.server
import ssl
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4443
CERT = "puzscan_cert.pem"
KEY = "puzscan_key.pem"

# Ensure cert/key exist
if not Path(CERT).is_file() or not Path(KEY).is_file():
    print(f"ERROR: Certificate or key not found in current directory. Expected {CERT} and {KEY}.")
    raise SystemExit(1)

handler = http.server.SimpleHTTPRequestHandler
httpd = http.server.HTTPServer(("0.0.0.0", PORT), handler)

# Wrap socket with SSL
httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               certfile=CERT,
                               keyfile=KEY,
                               ssl_version=ssl.PROTOCOL_TLS_SERVER)
print(f"Serving HTTPS on 0.0.0.0 port {PORT} (https://0.0.0.0:{PORT}/) ...")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Shutting down...")
    httpd.server_close()
