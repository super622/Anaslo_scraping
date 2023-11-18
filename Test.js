const http = require('http');
const { exec } = require('child_process');

// Replace with the appropriate port number of your Flask server
const serverPort = 5000;

const checkServerStatus = () => {
  const options = {
    hostname: '127.0.0.1',
    port: serverPort,
    path: '/',
    method: 'GET',
  };

  const req = http.request(options, (res) => {
    if (res.statusCode === 200) {
      console.log('Flask server is running');
    } else {
      console.log('Flask server is not running. Starting the server...');
      startFlaskServer();
    }
  });

  req.on('error', (err) => {
    console.log('Flask server is not running. Starting the server......');
    startFlaskServer();
  });

  req.end();
};

const startFlaskServer = () => {
    exec(__dirname + '\\start_1.bat', (err, stdout, stderr) => {
        if (err) {
            console.error(`Error starting Flask server: ${err}`);
            return;
        }
        console.log(stdout);
    });
    // const currentDir = __dirname;
    // exec('flask run -h 0.0.0.0', { cwd: currentDir }, (err, stdout, stderr) => {
    //     if (err) {
    //         console.error(`Error starting Flask server: ${err}`);
    //         return;
    //     }
    //     console.log(stdout);
    // });
};

// Check server status initially
checkServerStatus();

// Check server status every 2 seconds
setInterval(checkServerStatus, 2000);
