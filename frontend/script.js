const API_BASE = 'http://127.0.0.1:5000';

// ── Slider live update ───────────────────────────────────────
const slider = document.getElementById('num-images');
const countDisplay = document.getElementById('count-display');
slider.addEventListener('input', () => {
  countDisplay.textContent = slider.value;
});

// ── Main generate function ───────────────────────────────────
async function generateImages() {
  const btn = document.getElementById('generate-btn');
  const btnText = document.getElementById('btn-text');
  const grid = document.getElementById('image-grid');
  const statusBar = document.getElementById('status-bar');
  const numImages = parseInt(slider.value);
  const seedVal = document.getElementById('seed-input').value;

  // UI: loading state
  btn.disabled = true;
  btnText.textContent = 'Generating...';
  statusBar.className = 'status-bar';
  statusBar.textContent = `Sampling ${numImages} image${numImages > 1 ? 's' : ''} from latent space...`;

  // Show skeleton loaders
  grid.innerHTML = Array(numImages).fill('<div class="skeleton"></div>').join('');

  const body = { num_images: numImages };
  if (seedVal !== '') body.seed = parseInt(seedVal);

  try {
    const res = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!res.ok) throw new Error(`Server error: ${res.status}`);

    const data = await res.json();

    // Render images with staggered animation
    grid.innerHTML = '';
    data.images.forEach((b64, i) => {
      const img = document.createElement('img');
      img.src = `data:image/png;base64,${b64}`;
      img.alt = `Generated image ${i + 1}`;
      img.style.animationDelay = `${i * 40}ms`;
      img.title = `Image ${i + 1} · Click to open full size`;
      img.addEventListener('click', () => openFullSize(b64));
      grid.appendChild(img);
    });

    statusBar.className = 'status-bar success';
    statusBar.textContent = `✓ ${data.count} images generated · device: ${data.device}${data.seed !== null ? ' · seed: ' + data.seed : ''}`;

  } catch (err) {
    grid.innerHTML = '';
    statusBar.className = 'status-bar error';
    statusBar.textContent = `✗ ${err.message} — is the Flask server running?`;
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Generate';
  }
}

// ── Click image to open full size ───────────────────────────
function openFullSize(b64) {
  const win = window.open();
  win.document.write(`
    <html>
      <head><title>Generated Image</title>
      <style>body{margin:0;background:#0a0a0a;display:flex;align-items:center;justify-content:center;min-height:100vh;}
      img{image-rendering:pixelated;width:320px;height:320px;border-radius:4px;}</style></head>
      <body><img src="data:image/png;base64,${b64}" /></body>
    </html>
  `);
}