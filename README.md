# WGAN-CIFAR

A Wasserstein GAN trained on CIFAR-10, served via a Flask backend with a dynamic HTML/CSS/JS frontend.

## Project Structure
- `model/` — Colab training notebook and saved weights
- `backend/` — Flask API serving the Generator
- `frontend/` — Static HTML/CSS/JS interface
wgan-cifar/
├── model/
│   ├── wgan_cifar_training_.ipynb   # Colab training notebook
│   └── generator_final.pth          # Trained generator weights (not tracked by git)
├── backend/
│   ├── app.py                       # Flask inference server
│   └── requirements.txt             # Python dependencies
├── frontend/
│   ├── index.html                   # Main page
│   ├── style.css                    # Styles
│   └── script.js                    # Fetch + dynamic rendering
└── README.md

---

## Tech Stack

| Layer | Technology |
|---|---|
| Model Training | PyTorch, Google Colab (T4 GPU) |
| Dataset | CIFAR-10 (50,000 32×32 RGB images) |
| Backend | Flask, Flask-CORS |
| Frontend | HTML, CSS, Vanilla JS |
| Version Control | Git + GitHub |

---

## Model Architecture

### Generator
Takes a 128-dimensional noise vector and upsamples through four transposed convolution layers to produce a 32×32 RGB image.

Noise (128×1×1)
→ ConvTranspose2d → BatchNorm → ReLU   [512 ch, 4×4]
→ ConvTranspose2d → BatchNorm → ReLU   [256 ch, 8×8]
→ ConvTranspose2d → BatchNorm → ReLU   [128 ch, 16×16]
→ ConvTranspose2d → Tanh               [3 ch, 32×32]

### Critic
Mirrors the Generator with strided convolutions and Instance Normalisation. Outputs a raw scalar score (not a probability).
Image (3×32×32)
→ Conv2d → LeakyReLU                   [64 ch, 16×16]
→ Conv2d → InstanceNorm → LeakyReLU   [128 ch, 8×8]
→ Conv2d → InstanceNorm → LeakyReLU   [256 ch, 4×4]
→ Conv2d                               [1×1×1 scalar]

---

## Training Hyperparameters

| Parameter | Value | Reason |
|---|---|---|
| Latent Dim | 128 | Enough capacity for CIFAR diversity |
| Batch Size | 64 | Stable gradient estimates |
| Epochs | 100 | Sufficient convergence on CIFAR-10 |
| Learning Rate | 1e-4 | Standard for Adam on GANs |
| Critic Iterations | 5 | Critic trained 5× per generator step |
| Lambda GP | 10 | Gradient penalty weight (WGAN-GP standard) |
| β₁, β₂ (Adam) | 0.0, 0.9 | β₁=0 recommended for WGAN stability |

---

## Setup & Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/wgan-cifar.git
cd wgan-cifar
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows PowerShell
```

### 3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Add the model weights
Download `generator_final.pth` and place it in `model/`.

### 5. Run the Flask backend
```bash
cd backend
python app.py
```
Server runs at `http://127.0.0.1:5000`

### 6. Open the frontend
Open `frontend/index.html` with Live Server in VS Code.

---

## API Reference

### `GET /health`
Returns server status.
```json
{ "status": "ok", "device": "cpu" }
```

### `POST /generate`
Generates images from random noise.

**Request body:**
```json
{
  "num_images": 9,
  "seed": 42
}
```

**Response:**
```json
{
  "images": ["<base64 PNG>", "..."],
  "count": 9,
  "seed": 42,
  "device": "cpu"
}
```

---

## How WGAN-GP Differs from Vanilla GAN

| | Standard GAN | WGAN-GP |
|---|---|---|
| Loss | Binary Cross Entropy | Earth Mover's Distance |
| Output layer | Sigmoid (probability) | Raw scalar score |
| Training stability | Mode collapse prone | Stable gradients |
| Gradient control | None | Gradient penalty (λ=10) |
| Normalisation | BatchNorm in critic | InstanceNorm in critic |