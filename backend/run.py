import os
import sys
import logging
from app import app
from model.detector import setup_model_environment

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('screenguard.log')
        ]
    )

def check_environment():
    """Check if the environment is properly set up"""
    logger = logging.getLogger(__name__)
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check required directories
    required_dirs = ['models', 'uploads', 'temp']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logger.info(f"Created directory: {dir_name}")
    
    logger.info("Environment check completed successfully")

def main():
    """Main startup function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ScreenGuard Backend Server...")
    
    try:
        # Check environment
        check_environment()
        
        # Setup model environment
        setup_model_environment()
        
        # Start the Flask application
        logger.info("Server starting on http://127.0.0.1:5000")
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
