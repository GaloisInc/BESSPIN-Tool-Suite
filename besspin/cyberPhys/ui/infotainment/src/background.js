'use strict'

import { app, protocol, BrowserWindow, ipcMain } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import installExtension, { VUEJS_DEVTOOLS } from 'electron-devtools-installer'
const isDevelopment = process.env.NODE_ENV !== 'production'
import {CanListener, CanNetwork, CANID, CanMessage} from '../../common/can';
import {Config} from '../../common/config';
let can_net = new CanNetwork(5013);

let car_loc = {
  x: 0,
  y: 0,
  r: 0
};

can_net.register( new CanListener( (msg) => {
  // console.log("got message X", msg);
  car_loc.x = msg.getFloat();
}, [CANID.CAN_ID_CAR_X]));

can_net.register( new CanListener( (msg) => {
  car_loc.y = msg.getFloat();
}, [CANID.CAN_ID_CAR_Y]));

can_net.register( new CanListener( (msg) => {
  car_loc.r = msg.getFloat();
}, [CANID.CAN_ID_CAR_R]));

// Return current location when polled
ipcMain.on('can-loc-poll', (event) => {
    event.reply('can-loc-reply', car_loc.x, car_loc.y, car_loc.r);
})


ipcMain.on('volume-inc', () => {
  console.debug("volume dec");
  can_net.send(CanMessage.fromChar(CANID.CAN_ID_BUTTON_PRESSED,
    Config.BUTTON_VOLUME_UP).buffer());
})

ipcMain.on('volume-dec', () => {
  console.debug("volume dec");
  can_net.send(CanMessage.fromChar(CANID.CAN_ID_BUTTON_PRESSED,
    Config.BUTTON_VOLUME_DOWN).buffer());
})

ipcMain.on('channel-selected', (_, station) => {
  console.debug("channel selected ", station);
  can_net.send(CanMessage.fromChar(CANID.CAN_ID_BUTTON_PRESSED,
    station).buffer());
})


// Scheme must be registered before the app is ready
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])

async function createWindow() {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 800,
    height: 480,
    frame: false,
    autoHideMenuBar: true,
    kiosk: !isDevelopment,
    webPreferences: {
      nodeIntegration: true
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
