import io
import base64
import os
import torch
import torch.nn as nn
from torchvision.utils import make_grid
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image

app = Flask(__name__)
CORS(app)

# ─── Hyperparameters (must match training) ───────────────────
LATENT_DIM = 128
FEATURES_GEN = 64
CHANNELS = 3
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ─── Generator Architecture (copy from notebook) ─────────────
class Generator(nn.Module):
    def __init__(self, latent_dim, features, channels):
        super(Generator, self).__init__()
        self.net = nn.Sequential(
            self._block(latent_dim, features * 8, 4, 1, 0),
            self._block(features * 8, features * 4, 4, 2, 1),
            self._block(features * 4, features * 2, 4, 2, 1),
            nn.ConvTranspose2d(features * 2, channels, 4, 2, 1),
            nn.Tanh()
        )

    def _block(self, in_ch, out_ch, kernel, stride, padding):
        return nn.Sequential(
            nn.ConvTranspose2d(in_ch, out_ch, kernel, stride, padding, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.net(x)

# ─── Load Model Once at Startup ──────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'generator_final.pth')

gen = Generator(LATENT_DIM, FEATURES_GEN, CHANNELS).to(DEVICE)
gen.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
gen.eval()
print(f"Model loaded successfully on {DEVICE}")

# ─── Helper: tensor → base64 PNG ─────────────────────────────
def tensor_to_base64(tensor):
    # Denormalize from [-1, 1] to [0, 255]
    tensor = (tensor * 0.5 + 0.5).clamp(0, 1)
    tensor = (tensor * 255).byte().permute(1, 2, 0).cpu().numpy()
    img = Image.fromarray(tensor)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# ─── Routes ──────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'device': str(DEVICE)})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()

    # Parse params with defaults
    num_images = int(data.get('num_images', 9))
    seed = data.get('seed', None)

    # Clamp to safe range
    num_images = max(1, min(num_images, 16))

    # Optional reproducibility
    if seed is not None:
        torch.manual_seed(int(seed))

    with torch.no_grad():
        noise = torch.randn(num_images, LATENT_DIM, 1, 1, device=DEVICE)
        fake_images = gen(noise)

    # Convert each image to base64
    images_b64 = [tensor_to_base64(img) for img in fake_images]

    return jsonify({
        'images': images_b64,
        'count': num_images,
        'seed': seed,
        'device': str(DEVICE)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)