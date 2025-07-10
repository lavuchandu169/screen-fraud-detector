
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import numpy as np
from PIL import Image
import io
import base64
from werkzeug.utils import secure_filename
import logging

print("Starting Flask app import process...")

try:
    # Import model utilities
    print("Importing model utilities...")
    from model.detector import ImageAuthenticityDetector
    print("✓ ImageAuthenticityDetector imported successfully")
except Exception as e:
    print(f"❌ Error importing ImageAuthenticityDetector: {e}")
    exit(1)

print("Creating Flask app...")
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

print("Initializing detector...")
try:
    # Initialize the detector (will load IFAKE/PhotoHolmes model + transaction analyzer)
    detector = ImageAuthenticityDetector()
    print("✓ Detector initialized successfully")
except Exception as e:
    print(f"❌ Error initializing detector: {e}")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_file):
    """
    Preprocess uploaded image for model input
    Returns PIL Image object ready for analysis
    """
    try:
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Log image info
        logger.info(f"Image preprocessed: {image.size}, mode: {image.mode}")
        
        return image
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise ValueError(f"Invalid image file: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector.is_model_loaded(),
        'features_available': ['basic_detection', 'transaction_analysis', 'metadata_extraction'],
        'timestamp': time.time()
    })

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Main endpoint for comprehensive image authenticity analysis
    Expects: multipart/form-data with 'image' file
    Optional: 'transaction_mode' parameter (true/false)
    Returns: JSON with detailed analysis results
    """
    start_time = time.time()
    
    try:
        logger.info("=== Starting image analysis ===")
        
        # Check if image file is present
        if 'image' not in request.files:
            logger.error("No image file provided")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, JPEG allowed'}), 400
        
        # Check for transaction analysis mode
        transaction_mode = request.form.get('transaction_mode', 'true').lower() == 'true'
        
        # Secure filename
        filename = secure_filename(file.filename)
        logger.info(f"Processing file: {filename} (transaction_mode: {transaction_mode})")
        
        # Preprocess image
        image = preprocess_image(file)
        
        # Run comprehensive detection analysis
        logger.info("Starting tampering detection...")
        result = detector.detect_tampering(image, analyze_transactions=transaction_mode)
        logger.info(f"Detection completed. Result: {result.get('is_authentic', 'unknown')}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            'result': 'Original' if result.get('is_authentic', False) else 'Edited',
            'confidence': float(result.get('confidence', 0.0)),
            'processing_time': processing_time,
            'analysis_type': result.get('analysis_type', 'basic')
        }
        
        logger.info(f"Basic response prepared: {response['result']} with {response['confidence']:.3f} confidence")
        
        # Add basic details
        if 'details' in result:
            response['details'] = result['details']
        
        # Add tampered regions if detected
        if 'tampered_regions' in result and result['tampered_regions']:
            response['tampered_regions'] = result['tampered_regions']
        
        # Add comprehensive transaction analysis if available
        if 'transaction_analysis' in result:
            logger.info("Adding transaction analysis to response...")
            transaction_data = result['transaction_analysis']
            
            response['transaction_analysis'] = {
                'metadata_analysis': transaction_data.get('metadata_analysis', {}),
                'text_analysis': transaction_data.get('text_analysis', {}),
                'fraud_indicators': transaction_data.get('fraud_indicators', []),
                'recommendations': transaction_data.get('recommendations', []),
                'suspicious_regions': []
            }
            
            # Add pattern analysis results
            pattern_analysis = transaction_data.get('pattern_analysis', {})
            suspicious_regions = []
            
            # Collect all suspicious regions
            for copy_paste in pattern_analysis.get('copy_paste_regions', []):
                suspicious_regions.append({
                    'type': 'copy_paste',
                    'location': copy_paste.get('location', {}),
                    'size': copy_paste.get('size', {}),
                    'confidence': copy_paste.get('confidence', 0),
                    'description': copy_paste.get('description', '')
                })
            
            for resolution_issue in pattern_analysis.get('resolution_inconsistencies', []):
                suspicious_regions.append({
                    'type': 'resolution_inconsistency',
                    'severity': resolution_issue.get('severity', 'medium'),
                    'description': resolution_issue.get('description', ''),
                    'regions_affected': resolution_issue.get('regions_affected', 0)
                })
            
            response['transaction_analysis']['suspicious_regions'] = suspicious_regions
            
            # Add reverse search results
            reverse_search = transaction_data.get('reverse_search', {})
            if reverse_search.get('found_matches'):
                response['reverse_search'] = {
                    'found_matches': True,
                    'similar_images': reverse_search.get('similar_images', 0),
                    'earliest_occurrence': reverse_search.get('earliest_occurrence'),
                    'warnings': reverse_search.get('warnings', [])
                }
        
        logger.info(f"Final response prepared. Keys: {list(response.keys())}")
        logger.info(f"Analysis completed in {processing_time:.2f}s: {response['result']}")
        
        # Make sure we return a proper JSON response
        json_response = jsonify(response)
        logger.info("JSON response created successfully")
        return json_response
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        logger.exception("Full error traceback:")
        return jsonify({'error': 'Internal server error during analysis'}), 500

# ... keep existing code (remaining endpoints and error handlers)

if __name__ == '__main__':
    print("Starting Flask server...")
    try:
        app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")