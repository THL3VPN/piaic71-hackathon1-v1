#!/usr/bin/env python3
"""
Test script to verify database configuration works correctly without connecting to database.
"""
import os
from app.database.config import db_settings

print("Database configuration test:")
print(f"NEON_DATABASE_URL from .env: {os.getenv('NEON_DATABASE_URL', 'Not set')}")
print(f"DATABASE_URL from .env: {os.getenv('DATABASE_URL', 'Not set')}")
print(f"Database URL (from get_database_url): {db_settings.get_database_url()}")
print(f"Database host: {db_settings.database_host}")
print(f"Database port: {db_settings.database_port}")
print(f"Database name: {db_settings.database_name}")
print(f"Database user: {db_settings.database_user}")
print("Configuration loaded successfully!")