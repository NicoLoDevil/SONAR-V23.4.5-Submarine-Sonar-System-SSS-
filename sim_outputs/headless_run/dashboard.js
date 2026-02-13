document.addEventListener('DOMContentLoaded', () => {
  const frames = Array.from(document.querySelectorAll('.frame'));
  if (!frames.length) return;

  let idx = 0;
  let timer = null;
  let interval = 800;

  // hide all but first
  frames.forEach((f, i) => { if (i !== 0) f.style.display = 'none'; });

  const controls = document.createElement('div');
  controls.style.margin = '0.5rem 0';

  const playBtn = document.createElement('button'); playBtn.textContent = 'Play';
  const pauseBtn = document.createElement('button'); pauseBtn.textContent = 'Pause';
  const prevBtn = document.createElement('button'); prevBtn.textContent = 'Prev';
  const nextBtn = document.createElement('button'); nextBtn.textContent = 'Next';
  const speedLabel = document.createElement('label'); speedLabel.textContent = ' Speed (ms): ';
  const speedInput = document.createElement('input'); speedInput.type = 'number'; speedInput.value = interval; speedInput.min = 100; speedInput.max = 5000; speedInput.step = 100;

  controls.appendChild(prevBtn);
  controls.appendChild(playBtn);
  controls.appendChild(pauseBtn);
  controls.appendChild(nextBtn);
  controls.appendChild(speedLabel);
  controls.appendChild(speedInput);

  const framesContainer = document.querySelector('div');
  // insert controls before the frames container (after the H2)
  const h2 = document.querySelector('h2');
  if (h2 && h2.nextSibling) h2.parentNode.insertBefore(controls, h2.nextSibling);
  else document.body.insertBefore(controls, document.body.firstChild);

  function show(i) {
    frames.forEach((f, j) => { f.style.display = (j === i) ? '' : 'none'; });
    idx = i;
  }

  function next() { show((idx + 1) % frames.length); }
  function prev() { show((idx - 1 + frames.length) % frames.length); }

  function start() {
    if (timer) return;
    timer = setInterval(next, interval);
  }

  function stop() {
    if (!timer) return;
    clearInterval(timer); timer = null;
  }

  playBtn.addEventListener('click', start);
  pauseBtn.addEventListener('click', stop);
  nextBtn.addEventListener('click', () => { stop(); next(); });
  prevBtn.addEventListener('click', () => { stop(); prev(); });
  speedInput.addEventListener('change', (e) => {
    const v = parseInt(e.target.value, 10) || 800;
    interval = Math.max(100, v);
    if (timer) { stop(); start(); }
  });
});
