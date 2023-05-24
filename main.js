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

  const contents = main.webContents;
  console.log(contents.undo);

  // main.loadFile('./main/main.html');
  
}

app.on('ready', main)

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
})