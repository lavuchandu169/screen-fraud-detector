
# ScreenGuard Backend

AI-powered image authenticity detection backend using Flask and deep learning models.

## Features

- **Image Upload & Processing**: Secure file upload with validation
- **AI Detection**: Integration with IFAKE and PhotoHolmes models
- **REST API**: Clean endpoints for frontend integration
- **Real-time Analysis**: Fast processing with confidence scores
- **Detailed Results**: Tampering detection with highlighted regions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Models (Choose One)

#### Option A: IFAKE Model
```bash
# Download IFAKE model
git clone https://github.com/grip-unina/IFAKE.git
# Follow their setup instructions
# Copy model files to ./models/ifake_model.pth
```

#### Option B: PhotoHolmes Model
```bash
# Download PhotoHolmes model
git clone https://github.com/photoholmes/photoholmes.git
# Follow their setup instructions  
# Copy model files to ./models/photoholmes_model.pth
```

### 3. Run the Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### POST /analyze
Analyze an image for tampering detection.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `image` file (PNG, JPEG, max 10MB)

**Response:**
```json
{
  "result": "Original" | "Edited",
  "confidence": 0.92,
  "processing_time": 1.45,
  "details": "Analysis description",
  "tampered_regions": [
    {
      "x": 150,
      "y": 200,
      "width": 80,
      "height": 60,
      "confidence": 0.85
    }
  ]
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": 1694123456
}
```

### GET /model-info
Get information about the loaded model.

**Response:**
```json
{
  "model_type": "ifake",
  "model_loaded": true,
  "device": "cuda:0",
  "input_size": [224, 224],
  "status": "ready"
}
```

## Model Integration

### Adding IFAKE Model

1. Download the IFAKE repository:
```bash
git clone https://github.com/grip-unina/IFAKE.git
```

2. Install IFAKE dependencies:
```bash
cd IFAKE
pip install -e .
```

3. Update `model/detector.py`:
```python
from ifake.models import IFAKEDetector

def _load_model(self):
    self.model = IFAKEDetector.load_from_checkpoint(model_file)
    self.model.eval()
    self.model.to(self.device)
```

### Adding PhotoHolmes Model

1. Download the PhotoHolmes repository:
```bash
git clone https://github.com/photoholmes/photoholmes.git
```

2. Install PhotoHolmes dependencies:
```bash
cd photoholmes
pip install -e .
```

3. Update `model/detector.py`:
```python
from photoholmes.models import PhotoHolmesDetector

def _load_model(self):
    self.model = PhotoHolmesDetector.load_pretrained(model_file)
    self.model.eval()
    self.model.to(self.device)
```

## Directory Structure

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── model/
│   ├── detector.py       # Core detection logic
│   └── __init__.py
├── models/               # Model files (download separately)
│   ├── ifake_model.pth
│   └── photoholmes_model.pth
├── uploads/              # Temporary file storage
└── tests/                # Unit tests
```

## Configuration

Edit `config.py` to customize:

- **Model Settings**: Change default model type, paths
- **Security**: Update CORS origins, file size limits
- **Performance**: GPU settings, threading options

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

### Adding New Models

1. Create a new model class in `model/detector.py`
2. Add configuration in `model_configs`
3. Implement `_load_model()` and `detect_tampering()` methods
4. Update `requirements.txt` with model dependencies

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
export MODEL_PATH=/path/to/models
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Security Considerations

- **File Validation**: Only PNG/JPEG files accepted
- **Size Limits**: 10MB maximum file size
- **CORS**: Configured for specific origins
- **Input Sanitization**: Secure filename handling
- **Error Handling**: No sensitive information in error responses

## Performance Optimization

- **GPU Acceleration**: Automatic CUDA detection
- **Batch Processing**: Support for multiple images
- **Caching**: Model loaded once at startup
- **Async Processing**: Non-blocking request handling

## Troubleshooting

### Model Not Loading
- Check model file paths in `models/` directory
- Verify model file integrity
- Check PyTorch/CUDA compatibility

### CUDA Errors
- Verify CUDA installation: `torch.cuda.is_available()`
- Check GPU memory: `nvidia-smi`
- Use CPU fallback if needed

### Memory Issues
- Reduce batch size
- Enable gradient checkpointing
- Use smaller input image sizes

## License

This project is for educational purposes only. Model licenses apply separately.
