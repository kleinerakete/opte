// server_node.js - Express HTTPS example
// Requires Node.js and npm, install dependencies with: npm install express
// Run: node server_node.js [PORT]
const fs = require('fs');
const https = require('https');
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello from Node/Express over HTTPS!\n');
});

const port = process.argv[2] || 8443;
const options = {
  key: fs.readFileSync('puzscan_key.pem'),
  cert: fs.readFileSync('puzscan_cert.pem')
};
https.createServer(options, app).listen(port, '0.0.0.0', () => {
  console.log('Express HTTPS server listening on port', port);
});
