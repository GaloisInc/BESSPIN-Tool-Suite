'use strict'

import { app, protocol, BrowserWindow, ipcMain } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import installExtension, { VUEJS_DEVTOOLS } from 'electron-devtools-installer'
const isDevelopment = process.env.NODE_ENV !== 'production'
const { exec } = require("child_process");
import zmq, { socket } from 'zeromq';
const config = require('./config.js');

ipcMain.on('atem-switch', (event, ch) => {
  var atemexec = '/home/pi/build/BESSPIN-Tool-Suite/besspin/cyberPhys/ui/hacker-kiosk/atem-control.js';
  exec(`${atemexec} ${ch}`, (error, stdout, stderr) => {
    if (error) {
      console.log(`error: ${error.message}`);
      return;
  }
  if (stderr) {
    console.log(`stderr: ${stderr}`);
    return;
  }
    console.log(`stdout: ${stdout}`);
  })
})

// ZMQ Network
let zmq_address = config.ZMQ_ADDRESS;
console.log(config);
let zmq_sock = zmq.socket("req");
zmq_sock.connect(zmq_address);

let zmqQueue = [];

zmq_sock.on('message', (msg) => {
  let decoded = JSON.parse(msg);
  console.log("zmq message recieved: ", decoded);
  zmqQueue.push(decoded);
});

ipcMain.on('zmq-poll', (event) => {
  event.reply('zmq-results',  JSON.parse(JSON.stringify(zmqQueue)));
  zmqQueue = [];
});

ipcMain.on('button-pressed', (event, func, args) => {
  console.log('button-pressed', func, args);
  zmq_sock.send(JSON.stringify({'func': func, 'args': args}));
});

// Scheme must be registered before the app is ready
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])


async function createWindow() {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 1080,
    height: 1920,
    frame: false,
    autoHideMenuBar: true,
    kiosk: !isDevelopment,
    webPreferences: {
      nodeIntegration: true,
      devTools: isDevelopment,
    }
  })

  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Load the url of the dev server if in development mode
    await win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    if (!process.env.IS_TEST) win.webContents.openDevTools()
  } else {
    createProtocol('app')
    // Load the index.html when not in development
    win.loadURL('app://./index.html')
  }
}

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', async () => {
  if (isDevelopment && !process.env.IS_TEST) {
    // Install Vue Devtools
    try {
      await installExtension(VUEJS_DEVTOOLS)
    } catch (e) {
      console.error('Vue Devtools failed to install:', e.toString())
    }
  }
  createWindow()
})

// Exit cleanly on request from parent process in development mode.
if (isDevelopment) {
  if (process.platform === 'win32') {
    process.on('message', (data) => {
      if (data === 'graceful-exit') {
        app.quit()
      }
    })
  } else {
    process.on('SIGTERM', () => {
      app.quit()
    })
  }
}
