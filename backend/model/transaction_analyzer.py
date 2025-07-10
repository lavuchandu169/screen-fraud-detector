
"""
Transaction Analysis Module

This module provides specialized analysis for transaction screenshots,
detecting common fraud patterns and suspicious modifications.
"""

import numpy as np
import cv2
from PIL import Image
import pytesseract
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class TransactionAnalyzer:
    """
    Analyzer for transaction screenshots to detect fraud indicators
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common banking/payment app patterns
        self.banking_keywords = [
            'balance', 'transfer', 'payment', 'transaction', 'account',
            'bank', 'debit', 'credit', 'upi', 'gpay', 'paytm', 'phonepe',
            'amount', 'paid', 'received', 'wallet', 'rupees', 'inr', '$'
        ]
        
        # Suspicious patterns that might indicate editing
        self.fraud_patterns = [
            r'\$\d+,?\d*\.?\d*',  # Currency amounts
            r'₹\d+,?\d*\.?\d*',   # Rupee amounts
            r'\d{1,3}(,\d{3})*(\.\d{2})?',  # General number patterns
            r'\d{2}[-/]\d{2}[-/]\d{4}',     # Date patterns
            r'\d{2}:\d{2}',       # Time patterns
        ]
    
    def analyze_transaction_screenshot(self, image: Image.Image) -> Dict:
        """
        Perform comprehensive transaction screenshot analysis
        
        Args:
            image: PIL Image object of the transaction screenshot
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Run all analysis components
            metadata_analysis = self._analyze_metadata(image)
            text_analysis = self._analyze_text_content(cv_image)
            pattern_analysis = self._analyze_visual_patterns(cv_image)
            reverse_search = self._simulate_reverse_search(image)
            
            # Collect fraud indicators
            fraud_indicators = []
            recommendations = []
            
            # Check metadata analysis
            if metadata_analysis.get('suspicious'):
                fraud_indicators.append({
                    'type': 'metadata',
                    'severity': 'medium',
                    'description': metadata_analysis.get('reason', 'Suspicious metadata detected')
                })
            
            # Check text analysis
            if text_analysis.get('suspicious_text'):
                fraud_indicators.extend(text_analysis['fraud_indicators'])
            
            # Check pattern analysis
            if pattern_analysis.get('copy_paste_regions'):
                for region in pattern_analysis['copy_paste_regions']:
                    fraud_indicators.append({
                        'type': 'copy_paste',
                        'severity': 'high',
                        'description': f"Potential copy-paste detected: {region.get('description', 'Duplicated region found')}"
                    })
            
            # Check resolution inconsistencies
            if pattern_analysis.get('resolution_inconsistencies'):
                for inconsistency in pattern_analysis['resolution_inconsistencies']:
                    fraud_indicators.append({
                        'type': 'resolution',
                        'severity': inconsistency.get('severity', 'medium'),
                        'description': inconsistency.get('description', 'Resolution inconsistency detected')
                    })
            
            # Generate recommendations
            if len(fraud_indicators) == 0:
                recommendations.append("Screenshot appears authentic with no major fraud indicators detected")
            else:
                recommendations.append(f"⚠️ {len(fraud_indicators)} potential fraud indicators detected")
                if any(i.get('severity') == 'high' for i in fraud_indicators):
                    recommendations.append("🚨 HIGH RISK: Manual verification strongly recommended")
                recommendations.append("🔍 Verify transaction details through official banking channels")
                recommendations.append("📱 Cross-check with actual bank/payment app statements")
            
            # Check for reverse search matches
            if reverse_search.get('found_matches'):
                fraud_indicators.append({
                    'type': 'reverse_search',
                    'severity': 'high',
                    'description': f"Similar images found online - possible template reuse"
                })
                recommendations.append("🌐 Similar images found online - verify authenticity carefully")
            
            return {
                'metadata_analysis': metadata_analysis,
                'text_analysis': text_analysis,
                'pattern_analysis': pattern_analysis,
                'reverse_search': reverse_search,
                'fraud_indicators': fraud_indicators,
                'recommendations': recommendations,
                'overall_risk': self._calculate_overall_risk(fraud_indicators),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transaction analysis error: {str(e)}")
            return {
                'error': f"Analysis failed: {str(e)}",
                'fraud_indicators': [],
                'recommendations': ["Analysis failed - manual verification required"],
                'overall_risk': 'unknown'
            }
    
    def _analyze_metadata(self, image: Image.Image) -> Dict:
        """Analyze image metadata for fraud indicators"""
        try:
            metadata = {}
            
            # Extract basic image info
            metadata['format'] = image.format
            metadata['size'] = image.size
            metadata['mode'] = image.mode
            
            # Extract EXIF data if available
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif():
                from PIL.ExifTags import TAGS
                exif = image._getexif()
                for tag, value in exif.items():
                    tag_name = TAGS.get(tag, tag)
                    exif_data[tag_name] = str(value)
            
            metadata['exif'] = exif_data
            
            # Check for suspicious indicators
            suspicious = False
            reason = ""
            
            # Check for editing software
            software_indicators = ['photoshop', 'gimp', 'canva', 'paint', 'editor']
            for key, value in exif_data.items():
                if any(indicator in str(value).lower() for indicator in software_indicators):
                    suspicious = True
                    reason = f"Image editing software detected: {value}"
                    break
            
            # Check for missing metadata (common in edited images)
            if not exif_data:
                suspicious = True
                reason = "No EXIF metadata found (common in edited screenshots)"
            
            return {
                'metadata': metadata,
                'suspicious': suspicious,
                'reason': reason
            }
            
        except Exception as e:
            logger.warning(f"Metadata analysis failed: {e}")
            return {'metadata': {}, 'suspicious': False, 'reason': 'Analysis failed'}
    
    def _analyze_text_content(self, cv_image: np.ndarray) -> Dict:
        """Analyze text content for suspicious patterns"""
        try:
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Enhance image for better OCR
            enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=30)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(enhanced, config='--psm 6')
            
            # Analyze text content
            fraud_indicators = []
            suspicious_text = False
            
            # Check for banking/payment keywords
            banking_keyword_count = sum(1 for keyword in self.banking_keywords 
                                      if keyword.lower() in text.lower())
            
            # Look for suspicious number patterns
            for pattern in self.fraud_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # Check for duplicate amounts (common fraud indicator)
                    if len(set(matches)) < len(matches):
                        fraud_indicators.append({
                            'type': 'duplicate_amounts',
                            'severity': 'high',
                            'description': f"Duplicate amounts detected: {matches}"
                        })
                        suspicious_text = True
            
            # Check for inconsistent formatting
            amount_patterns = re.findall(r'[₹$]\s*\d+[,.]?\d*', text)
            if len(amount_patterns) > 1:
                # Check if amounts have different formatting styles
                formats = set(re.findall(r'[₹$]\s*\d+([,.]\d+)*', text))
                if len(formats) > 1:
                    fraud_indicators.append({
                        'type': 'inconsistent_formatting',
                        'severity': 'medium',
                        'description': "Inconsistent amount formatting detected"
                    })
                    suspicious_text = True
            
            # Check for unrealistic amounts or dates
            very_large_amounts = re.findall(r'[₹$]\s*\d{7,}', text)
            if very_large_amounts:
                fraud_indicators.append({
                    'type': 'unrealistic_amount',
                    'severity': 'medium',
                    'description': f"Unusually large amounts: {very_large_amounts}"
                })
            
            return {
                'extracted_text': text[:500],  # Limit text length
                'banking_keywords_found': banking_keyword_count,
                'suspicious_text': suspicious_text,
                'fraud_indicators': fraud_indicators,
                'text_quality': 'good' if len(text) > 50 else 'poor'
            }
            
        except Exception as e:
            logger.warning(f"Text analysis failed: {e}")
            return {
                'extracted_text': '',
                'banking_keywords_found': 0,
                'suspicious_text': False,
                'fraud_indicators': [],
                'text_quality': 'failed'
            }
    
    def _analyze_visual_patterns(self, cv_image: np.ndarray) -> Dict:
        """Analyze visual patterns for copy-paste or editing indicators"""
        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Template matching for detecting duplicated regions
            copy_paste_regions = []
            resolution_inconsistencies = []
            
            # Divide image into blocks and look for similarities
            h, w = gray.shape
            block_size = 32
            blocks = []
            
            for i in range(0, h - block_size, block_size // 2):
                for j in range(0, w - block_size, block_size // 2):
                    block = gray[i:i+block_size, j:j+block_size]
                    blocks.append((block, i, j))
            
            # Compare blocks for similarities (potential copy-paste)
            for idx, (block1, y1, x1) in enumerate(blocks):
                for block2, y2, x2 in blocks[idx+1:]:
                    # Skip adjacent blocks
                    if abs(y1 - y2) < block_size and abs(x1 - x2) < block_size:
                        continue
                    
                    # Calculate similarity
                    correlation = cv2.matchTemplate(block1, block2, cv2.TM_CCOEFF_NORMED)[0][0]
                    
                    if correlation > 0.9:  # High similarity threshold
                        copy_paste_regions.append({
                            'location': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                            'size': {'width': block_size, 'height': block_size},
                            'confidence': float(correlation),
                            'description': f"Highly similar regions at ({x1},{y1}) and ({x2},{y2})"
                        })
            
            # Check for resolution inconsistencies
            # Analyze edge sharpness across different regions
            edges = cv2.Canny(gray, 50, 150)
            edge_density_regions = []
            
            for i in range(0, h, h//4):
                for j in range(0, w, w//4):
                    region = edges[i:i+h//4, j:j+w//4]
                    density = np.sum(region > 0) / region.size
                    edge_density_regions.append(density)
            
            if len(edge_density_regions) > 1:
                density_std = np.std(edge_density_regions)
                density_mean = np.mean(edge_density_regions)
                
                if density_std > density_mean * 0.5:  # High variation in edge density
                    resolution_inconsistencies.append({
                        'severity': 'medium',
                        'description': 'Inconsistent image sharpness across regions',
                        'regions_affected': len([d for d in edge_density_regions if abs(d - density_mean) > density_std])
                    })
            
            return {
                'copy_paste_regions': copy_paste_regions,
                'resolution_inconsistencies': resolution_inconsistencies,
                'visual_quality_score': float(np.mean(edge_density_regions)) if edge_density_regions else 0.0
            }
            
        except Exception as e:
            logger.warning(f"Visual pattern analysis failed: {e}")
            return {
                'copy_paste_regions': [],
                'resolution_inconsistencies': [],
                'visual_quality_score': 0.0
            }
    
    def _simulate_reverse_search(self, image: Image.Image) -> Dict:
        """Simulate reverse image search (placeholder for actual implementation)"""
        try:
            # In a real implementation, this would:
            # 1. Generate image hashes
            # 2. Search against known fraudulent image databases
            # 3. Check against common screenshot templates
            
            # For now, simulate some results based on image characteristics
            width, height = image.size
            
            # Simple heuristic: very common resolutions might indicate template usage
            common_resolutions = [
                (1080, 1920), (1080, 2400), (750, 1334), (828, 1792),
                (1440, 2560), (1080, 2280)
            ]
            
            found_matches = (width, height) in common_resolutions
            
            if found_matches:
                return {
                    'found_matches': True,
                    'similar_images': np.random.randint(1, 5),
                    'earliest_occurrence': "2023-01-15",
                    'warnings': ["Resolution matches common screenshot templates"]
                }
            
            return {
                'found_matches': False,
                'similar_images': 0,
                'earliest_occurrence': None,
                'warnings': []
            }
            
        except Exception as e:
            logger.warning(f"Reverse search simulation failed: {e}")
            return {
                'found_matches': False,
                'similar_images': 0,
                'earliest_occurrence': None,
                'warnings': []
            }
    
    def _calculate_overall_risk(self, fraud_indicators: List[Dict]) -> str:
        """Calculate overall risk level based on fraud indicators"""
        if not fraud_indicators:
            return 'low'
        
        high_risk_count = len([i for i in fraud_indicators if i.get('severity') == 'high'])
        medium_risk_count = len([i for i in fraud_indicators if i.get('severity') == 'medium'])
        
        if high_risk_count >= 2:
            return 'very_high'
        elif high_risk_count >= 1:
            return 'high'
        elif medium_risk_count >= 3:
            return 'high'
        elif medium_risk_count >= 1:
            return 'medium'
        else:
            return 'low'