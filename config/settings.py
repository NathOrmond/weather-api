"""
Configuration settings for the application.
"""

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'dev-key-change-in-production'
    # Add other configuration as needed


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True


class ProductionConfig(Config):
    """Production configuration."""
    SECRET_KEY = 'production-key-should-be-set-from-environment'
    # Set other production settings


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
