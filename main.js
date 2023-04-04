const { app, BrowserWindow } = require('electron');
const path = require('path');

function main() {

  const main = new BrowserWindow({
    title: "Open Show Cue Systems",
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js")
    }
  });

  main.loadFile('./main/main.html');

  // const presenter = new BrowserWindow({
  //   title: "OSCS Presenter View",
  //   frame: false,
  //   fullscreen: true
  // });

  // presenter.loadFile('./presenter/presenter.html');
  
}

app.on('ready', main)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
})