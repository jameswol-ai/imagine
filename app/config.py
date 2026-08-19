"""
IMAGINE
Application Configuration
"""

from .settings import settings


class AppConfig:
    API_PREFIX = settings.API_V1_PREFIX
    PROJECT_NAME = settings.APP_NAME
    DEBUG = settings.DEBUG


config = AppConfig()