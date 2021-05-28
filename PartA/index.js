const isAndroidWebView = (userAgent) => userAgent.includes('; wv');

const isIOSWebView = (userAgent) => userAgent.includes('Mobile/') && !userAgent.includes('Safari');

const isiPhone = (userAgent) => userAgent.includes('iPhone');

const isiPad = (userAgent) => userAgent.includes('iPad');

const isiPod = (userAgent) => userAgent.includes('iPod');

const isAndroid = (userAgent) => userAgent.includes('Android');

const isMac = (userAgent) => userAgent.includes('Mac');

const isWin = (userAgent) => userAgent.includes('Win');

const isMobileDevice = (userAgent) => isAndroid(userAgent) || isiPhone(userAgent) || isiPod(userAgent) || isiPad(userAgent);

const isMobileWebView = (userAgent) => isAndroidWebView(userAgent) || isIOSWebView(userAgent);

const getDeviceName = (userAgent) => 
    isiPhone(userAgent) ? 'iPhone' :
    isiPad(userAgent) ? 'iPad' :
    isiPod(userAgent) ? 'iPod' :
    isAndroid(userAgent) ? 'Android' :
    isMac(userAgent) ? 'PC (Mac)' :
    'PC (Windows)';

let http = require('http');
let server = http.createServer(function(req) {
        let userAgent = req.headers['user-agent'];
        let mobile = isMobileDevice(userAgent);
        let hostType = 'desktop-browser';
        let deviceType = 'desktop';
        let deviceName = getDeviceName(userAgent);
        if(mobile) {
            hostType = 'mobile-browser';
            let modileWebView = isMobileWebView(userAgent);
            if(modileWebView) {
                hostType = 'mobile-webview';
            }
        }
        console.log(
        'Host Type: ' + hostType + '\n' + 
        'Device Type: ' + deviceType + '\n' + 
        'Device Name: ' + deviceName);
        process.kill(process.pid, 'SIGTERM')
    });
  
  server.listen(3000, 'localhost');
  var url = 'http://localhost:3000';
  var start = (process.platform == 'darwin' ? 'open': process.platform == 'win32' ? 'start': 'xdg-open');
  require('child_process').exec(start + ' ' + url);