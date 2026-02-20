# PuZScan Keystore Bundle - Starter Launchers

This bundle now includes three ways to run a small HTTPS server using the included `puzscan_cert.pem` and `puzscan_key.pem`:

1) `demo` — Minimal Python stdlib HTTPS server (no extra dependencies). Default port 4443.
   - Start: `./run.sh demo 4443` or `./start.sh 4443`

2) `flask` — Flask app using the cert/key. Requires Python and `flask` package.
   - Install: `python3 -m pip install flask`
   - Start: `./run.sh flask 8443` or `./start_flask.sh 8443`

3) `node` — Node.js + Express HTTPS app. Requires Node.js and npm.
   - Install: `npm install`
   - Start: `./run.sh node 8443` or `./start_node.sh 8443`

Unified launcher: `./run.sh [demo|flask|node] [PORT]`

WARNING: These are demo/test servers only. Do not use in production without proper security review.
