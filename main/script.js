// mouse position
let mouse = {
  x: 0,
  y: 0
}

// state of the volume slider
let volume = {
  seeker: document.querySelector("div.devices.seeker"),
  track: document.querySelector("div.devices.track"),
  clicked: false,
  value: 0
}

// state of the player slider
let player = {
  seeker: document.querySelector("div.status.scrubber"),
  track: document.querySelector("div.status.line"),
  clicked: false,
  value: 0
}

// add mouse event listeners
volume.seeker.addEventListener('mousedown', () => {
  volume.clicked = true;
});
player.seeker.addEventListener('mousedown', () => {
  player.clicked = true;
});
document.addEventListener('mouseup', () => {
  volume.clicked = false;
  player.clicked = false;
});

// keep track of mouse position
document.addEventListener('mousemove', (e) => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
});

// every ms
setInterval(() => {

  // if the volume slider is selected
  if (volume.clicked) {

    // keep track of coordinates
    let x = mouse.x;
    let bounds = volume.track.getBoundingClientRect();
    let endpoints = [bounds.x, bounds.x + bounds.width];
    
    // lerp
    if (x > endpoints[1]) {
      volume.seeker.style.left = "95%";
    }
    else if (x < endpoints[0]) {
      volume.seeker.style.left = "3%";
      volume.value = 0;
    }
    else {
      let amount = (x - (endpoints[0] - 3)) / bounds.width;
      volume.value = amount;
      volume.seeker.style.left = amount * 92 + 3 + "%";
    }
  }

  // if the player slider is selected
  if (player.clicked) {

    // keep track of coordinates
    let x = mouse.x;
    let bounds = player.track.getBoundingClientRect();
    let endpoints = [bounds.x, bounds.x + bounds.width];
    
    // lerp
    if (x > endpoints[1]) {
      player.seeker.style.left = "100%";
    }
    else if (x < endpoints[0]) {
      player.seeker.style.left = "0%";
      player.value = 0;
    }
    else {
      let amount = (x - (endpoints[0])) / bounds.width;
      player.value = amount;
      player.seeker.style.left = amount * 100 + "%";
    }
  }
})