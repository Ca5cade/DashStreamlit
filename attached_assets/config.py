"""Application configuration."""
import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Generate a good secret key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-make-it-long-and-random')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_TYPE = 'filesystem'
    
    # Flask-Login configuration
    LOGIN_DISABLED = False
    LOGIN_VIEW = '/login'
    
    # Other configurations
    DEBUG = False
    TESTING = False