# app_flask.py - Flask HTTPS example
# Run: python3 app_flask.py [PORT]
from flask import Flask, send_from_directory
import ssl, sys, os
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from Flask over HTTPS!\n"

@app.route('/files/<path:filename>')
def files(filename):
    return send_from_directory('.', filename, as_attachment=False)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
    cert = 'puzscan_cert.pem'
    key = 'puzscan_key.pem'
    if not os.path.exists(cert) or not os.path.exists(key):
        raise SystemExit('Missing cert/key files')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert, keyfile=key)
    app.run(host='0.0.0.0', port=port, ssl_context=context)
