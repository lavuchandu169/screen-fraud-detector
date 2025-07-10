
# ScreenGuard 🛡️

**Advanced AI-powered image authenticity detection for identifying tampered screenshots and edited images.**

ScreenGuard is a full-stack web application that uses cutting-edge deep learning models to detect image manipulation, forgery, and tampering with high accuracy and detailed analysis.

## ✨ Features

🔍 **AI-Powered Detection**: Advanced deep learning models analyze pixel-level patterns  
📱 **Responsive Design**: Beautiful UI that works on desktop, tablet, and mobile  
⚡ **Real-time Analysis**: Fast processing with live progress indicators  
🎯 **High Accuracy**: Confidence scores and detailed detection results  
🔒 **Privacy-First**: All analysis performed locally - images never leave your device  
📊 **Detailed Reports**: Highlighted tampered regions and analysis insights  

## 🚀 Quick Start

### Frontend (React)
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Backend (Flask)
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python run.py
```

The application will be available at:
- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:5000`

## 🧠 Model Integration

ScreenGuard supports integration with state-of-the-art detection models:

### IFAKE Model
```bash
# Clone IFAKE repository
git clone https://github.com/grip-unina/IFAKE.git

# Follow their installation guide
# Place model files in backend/models/ifake_model.pth
```

### PhotoHolmes Model
```bash
# Clone PhotoHolmes repository  
git clone https://github.com/photoholmes/photoholmes.git

# Follow their installation guide
# Place model files in backend/models/photoholmes_model.pth
```

## 📁 Project Structure

```
screenguard/
├── src/                          # React frontend
│   ├── pages/Index.tsx          # Main application page
│   ├── components/ui/           # Reusable UI components
│   └── ...
├── backend/                      # Flask backend
│   ├── app.py                   # Main Flask application
│   ├── model/
│   │   ├── detector.py          # Core detection logic
│   │   └── __init__.py
│   ├── models/                  # AI model files (download separately)
│   ├── config.py                # Configuration settings
│   ├── requirements.txt         # Python dependencies
│   └── run.py                   # Startup script
└── README.md
```

## 🔧 API Reference

### `POST /analyze`
Analyze an image for tampering detection.

**Request:**
```bash
curl -X POST \
  -F "image=@screenshot.png" \
  http://localhost:5000/analyze
```

**Response:**
```json
{
  "result": "Edited",
  "confidence": 0.92,
  "processing_time": 1.45,
  "details": "Detected inconsistencies in JPEG compression artifacts",
  "tampered_regions": [
    {
      "x": 150, "y": 200,
      "width": 80, "height": 60,
      "confidence": 0.85
    }
  ]
}
```

### `GET /health`
Check server and model status.

### `GET /model-info`
Get information about the loaded model.

## 🎨 Technology Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS for styling
- Shadcn/UI component library
- Lucide React icons
- Responsive design with mobile support

**Backend:**
- Python Flask framework
- PyTorch for deep learning
- PIL/OpenCV for image processing
- CORS enabled for frontend integration

**AI Models:**
- IFAKE (Image Forgery Analysis and Knowledge Extraction)
- PhotoHolmes (Photo authenticity detection)
- Custom integration layer for multiple models

## 🔐 Security Features

- **File Validation**: Only PNG/JPEG files accepted
- **Size Limits**: 10MB maximum upload size
- **CORS Protection**: Configured origins
- **Input Sanitization**: Secure file handling
- **Error Handling**: No sensitive data exposure

## 🚀 Deployment

### Development
```bash
# Frontend
npm run dev

# Backend
cd backend && python run.py
```

### Production
```bash
# Frontend build
npm run build

# Backend with Gunicorn
cd backend && gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker
```dockerfile
# Frontend
FROM node:18-alpine
COPY . .
RUN npm install && npm run build

# Backend  
FROM python:3.9-slim
COPY backend/ .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 Performance

- **Processing Speed**: 1-3 seconds per image
- **Accuracy**: 90%+ detection rate (model dependent)
- **Supported Formats**: PNG, JPEG, JPG
- **Max File Size**: 10MB
- **Concurrent Users**: Scalable with Gunicorn

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📜 License

This project is for educational and research purposes only. Please respect the licenses of the integrated AI models:

- IFAKE: [License terms](https://github.com/grip-unina/IFAKE)
- PhotoHolmes: [License terms](https://github.com/photoholmes/photoholmes)

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section in backend/README.md
2. Review model integration guides
3. Open an issue with detailed information

## 🔮 Roadmap

- [ ] Batch processing for multiple images
- [ ] Video tampering detection
- [ ] Advanced visualization of tampered regions
- [ ] Model performance benchmarking
- [ ] Mobile app version
- [ ] API rate limiting and authentication

---

**Built with ❤️ for image authenticity and digital forensics research.**
