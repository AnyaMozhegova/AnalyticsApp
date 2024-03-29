const http = require('http');
const fs = require('fs');

const hostname = '0.0.0.0';
const port = 8000;

const server = http.createServer((req, response) => {
    console.log(`Serving request for ${req.url}`);
    let filePath;

    const reportRegEx = /^\/report\/(\d+)$/;

    if (reportRegEx.test(req.url)) {
        filePath = './html/report.html';
    } else if (req.url.endsWith('.css') || req.url.endsWith('.js') || req.url.endsWith('.ico')) {
        filePath = `.${req.url}`;
    } else {
        filePath = `./html${req.url === '/' ? '/index.html' : req.url}`;
        if (!filePath.endsWith('.html')) {
            filePath += '.html';
        }
    }

    fs.readFile(filePath, (error, data) => {
        if (error) {
            console.error(`Error reading file: ${error}`);
            response.writeHead(404, {'Content-Type': 'text/plain'});
            response.end('File not found');
        } else {
            const contentType = filePath.endsWith(".css") ? 'text/css' : 'text/html';
            response.writeHead(200, {'Content-Type': contentType});
            response.end(data);
        }
    });
});

server.listen(port, hostname, (error) => {
    if (error) {
        console.error(`Error: ${error}`);
    } else {
        console.log(`Server running at http://${hostname}:${port}`);
    }
});
