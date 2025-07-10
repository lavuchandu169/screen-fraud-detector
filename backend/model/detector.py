
"""
Image Authenticity Detector Module

This module provides the core functionality for detecting image tampering
using deep learning models like IFAKE or PhotoHolmes.
"""

import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import logging
import os
import json
from typing import Dict, List, Optional, Tuple

# Import our simple detector and transaction analyzer
from .simple_detector import SimpleImageDetector
from .transaction_analyzer import TransactionAnalyzer

logger = logging.getLogger(__name__)

def setup_model_environment():
    """Setup the model environment and download instructions"""
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        logger.info(f"Created models directory: {models_dir}")
    
    # Check for model files
    ifake_model = os.path.join(models_dir, "ifake_model.pth")
    photoholmes_model = os.path.join(models_dir, "photoholmes_model.pth")
    
    if not os.path.exists(ifake_model) and not os.path.exists(photoholmes_model):
        logger.info("No advanced model files found - using simple CV detector")
        logger.info("For advanced models:")
        logger.info("1. Research paper implementations may require specific setup")
        logger.info("2. Current detector uses computer vision techniques")
        logger.info("3. Provides real tampering detection capabilities")

class ImageAuthenticityDetector:
    """
    Main detector class for image authenticity analysis
    
    This class integrates:
    - Simple CV Detector: Real computer vision-based tampering detection
    - Transaction Analyzer: Specialized analysis for transaction screenshots
    - Mock Detector: Fallback for demonstration
    """
    
    def __init__(self, model_path: str = "models/", model_type: str = "simple"):
        """
        Initialize the detector
        
        Args:
            model_path: Path to the model files
            model_type: Type of model to use ('simple', 'ifake', or 'photoholmes')
        """
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.is_loaded = False
        
        # Initialize components
        self.simple_detector = SimpleImageDetector()
        self.transaction_analyzer = TransactionAnalyzer()
        
        # Model-specific configurations
        self.model_configs = {
            'simple': {
                'input_size': (512, 512),
                'model_file': None,
                'description': 'Computer vision-based tampering detection'
            },
            'ifake': {
                'input_size': (224, 224),
                'model_file': 'ifake_model.pth',
                'config_file': 'ifake_config.json',
                'download_url': 'Research paper implementation required'
            },
            'photoholmes': {
                'input_size': (256, 256),
                'model_file': 'photoholmes_model.pth',
                'config_file': 'photoholmes_config.json',
                'download_url': 'Research paper implementation required'
            }
        }
        
        # Initialize transforms
        self._setup_transforms()
        
        # Load model
        self._load_model()
    
    def _setup_transforms(self):
        """Setup image preprocessing transforms"""
        config = self.model_configs[self.model_type]
        
        if self.model_type == 'simple':
            # Simple detector works with original images
            self.transform = transforms.Compose([
                transforms.Resize(config['input_size']),
                transforms.ToTensor()
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(config['input_size']),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
    
    def _load_model(self):
        """Load the specified model"""
        try:
            if self.model_type == 'simple':
                # Simple detector is always available
                self.model = "simple_cv_detector"
                self.is_loaded = True
                logger.info("Simple computer vision detector loaded successfully")
                return
            
            # For advanced models
            config = self.model_configs[self.model_type]
            model_file = os.path.join(self.model_path, config['model_file'])
            
            if not os.path.exists(model_file):
                logger.warning(f"Advanced model file not found: {model_file}")
                logger.info(f"Falling back to simple detector")
                self.model_type = 'simple'
                self.model = "simple_cv_detector"
                self.is_loaded = True
                return
            
            # TODO: Load advanced models when available
            # This would require the specific model implementations
            logger.info(f"Advanced model loading not yet implemented for {self.model_type}")
            logger.info("Using simple detector instead")
            
            # Fallback to simple detector
            self.model_type = 'simple'
            self.model = "simple_cv_detector"
            self.is_loaded = True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            logger.info("Falling back to simple detector")
            self.model_type = 'simple'
            self.model = "simple_cv_detector"
            self.is_loaded = True
    
    def detect_tampering(self, image: Image.Image, analyze_transactions: bool = True) -> Dict:
        """
        Detect tampering in the provided image with optional transaction analysis
        
        Args:
            image: PIL Image object
            analyze_transactions: Whether to perform transaction-specific analysis
            
        Returns:
            Dictionary with detection results including transaction analysis
        """
        try:
            if not self.is_loaded:
                raise RuntimeError("Model not loaded")
            
            # Basic authenticity detection using simple detector
            if self.model == "simple_cv_detector":
                basic_result = self.simple_detector.detect_tampering(image)
                logger.info(f"Simple detector result: {'Authentic' if basic_result['is_authentic'] else 'Tampered'} "
                           f"(confidence: {basic_result['confidence']:.3f})")
            else:
                # TODO: Use advanced model when available
                basic_result = self.simple_detector.detect_tampering(image)
            
            # Add transaction-specific analysis if requested
            if analyze_transactions:
                logger.info("Performing transaction-specific analysis...")
                transaction_analysis = self.transaction_analyzer.analyze_transaction_screenshot(image)
                
                # Merge results
                result = {
                    **basic_result,
                    'transaction_analysis': transaction_analysis,
                    'analysis_type': 'comprehensive'
                }
                
                # Update overall confidence based on transaction analysis
                if 'fraud_indicators' in transaction_analysis:
                    fraud_count = len(transaction_analysis['fraud_indicators'])
                    high_risk_count = len([i for i in transaction_analysis['fraud_indicators'] 
                                         if i.get('severity') == 'high'])
                    
                    if high_risk_count > 0:
                        # Reduce confidence significantly for high-risk indicators
                        result['confidence'] = min(result['confidence'] * 0.3, 0.5)
                        result['is_authentic'] = False
                        result['details'] = f"HIGH RISK: {high_risk_count} critical fraud indicators detected"
                    elif fraud_count > 2:
                        # Moderate confidence reduction for multiple indicators
                        result['confidence'] = result['confidence'] * 0.6
                        result['details'] = f"MODERATE RISK: {fraud_count} suspicious patterns found"
            else:
                result = basic_result
                result['analysis_type'] = 'basic'
            
            return result
            
        except Exception as e:
            logger.error(f"Detection error: {str(e)}")
            raise RuntimeError(f"Detection failed: {str(e)}")
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        config = self.model_configs[self.model_type]
        
        return {
            'model_type': self.model_type,
            'model_loaded': self.is_loaded,
            'device': str(self.device),
            'input_size': config['input_size'],
            'description': config.get('description', 'Advanced ML model'),
            'status': 'ready' if self.is_loaded else 'not_loaded',
            'features': [
                'Real tampering detection' if self.model_type == 'simple' else 'Advanced ML detection',
                'Transaction screenshot analysis',
                'JPEG compression analysis',
                'Noise pattern detection',
                'Edge consistency analysis',
                'Metadata extraction'
            ]
        }
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded and ready"""
        return self.is_loaded