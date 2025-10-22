import sys
from loguru import logger
import os
from datetime import datetime

def setup_logger():
    """Setup comprehensive logging configuration"""
    
    # Remove default handler
    logger.remove()
    
    # Console logging with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File logging for errors
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days"
    )
    
    # File logging for all logs
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="50 MB",
        retention="7 days"
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logger.info("🚀 Logger initialized successfully")
    logger.info(f"📁 Log files will be saved to: {os.path.abspath('logs')}")
    
    return logger

def log_api_call(endpoint: str, method: str, user_id: str = None, **kwargs):
    """Log API calls with context"""
    logger.info(f"🌐 API Call: {method} {endpoint}")
    if user_id:
        logger.info(f"👤 User ID: {user_id}")
    if kwargs:
        logger.info(f"📝 Parameters: {kwargs}")

def log_error(error: Exception, context: str = ""):
    """Log errors with context"""
    logger.error(f"❌ Error in {context}: {str(error)}")
    logger.error(f"🔍 Error type: {type(error).__name__}")

def log_success(message: str, context: str = ""):
    """Log success messages"""
    logger.success(f"✅ {context}: {message}")

def log_ai_interaction(prompt: str, response: str, model: str = "gemini"):
    """Log AI interactions"""
    logger.info(f"🤖 AI Interaction - Model: {model}")
    logger.info(f"📝 Prompt: {prompt[:100]}...")
    logger.info(f"💬 Response: {response[:100]}...")

def log_database_operation(operation: str, table: str, **kwargs):
    """Log database operations"""
    logger.info(f"🗄️ Database: {operation} on {table}")
    if kwargs:
        logger.info(f"📊 Data: {kwargs}")

def log_file_operation(operation: str, filename: str, **kwargs):
    """Log file operations"""
    logger.info(f"📁 File {operation}: {filename}")
    if kwargs:
        logger.info(f"📊 Details: {kwargs}")

# Initialize logger
setup_logger()
