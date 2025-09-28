"""Deployment helpers for running the dashboard on Streamlit Cloud and beyond."""

import streamlit as st
import os
from pathlib import Path

class DeploymentConfig:
    """Utility class that abstracts deployment specific defaults."""
    
    def __init__(self):
        self.environment = self.detect_environment()
        self.config = self.load_config()
    
    def detect_environment(self):
        """Detect the runtime environment."""
        if "STREAMLIT_SHARING" in os.environ:
            return "streamlit_cloud"
        elif "HEROKU" in os.environ:
            return "heroku"
        elif "GOOGLE_CLOUD_PROJECT" in os.environ:
            return "gcp"
        elif "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
            return "aws"
        else:
            return "local"
    
    def load_config(self):
        """Load environment-specific defaults."""
        configs = {
            "local": {
                "debug": True,
                "cache_ttl": 300,
                "max_upload_size": 200,  # MB
                "show_raw_data": True,
                "log_level": "DEBUG"
            },
            "streamlit_cloud": {
                "debug": False,
                "cache_ttl": 3600,
                "max_upload_size": 100,  # MB
                "show_raw_data": True,
                "log_level": "INFO"
            },
            "heroku": {
                "debug": False,
                "cache_ttl": 1800,
                "max_upload_size": 50,  # MB
                "show_raw_data": False,
                "log_level": "WARNING"
            },
            "gcp": {
                "debug": False,
                "cache_ttl": 3600,
                "max_upload_size": 200,  # MB
                "show_raw_data": True,
                "log_level": "INFO"
            },
            "aws": {
                "debug": False,
                "cache_ttl": 1800,
                "max_upload_size": 100,  # MB
                "show_raw_data": False,
                "log_level": "INFO"
            }
        }
        
        return configs.get(self.environment, configs["local"])
    
    def setup_page_config(self):
        """Configure the default Streamlit page metadata."""
        st.set_page_config(
            page_title="Ads Analyzer",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/avnergomes/ads-analyzer',
                'Report a bug': 'https://github.com/avnergomes/ads-analyzer/issues',
                'About': "Ads Analyzer - Integrated advertising and ticket analytics"
            }
        )

    def setup_caching(self):
        """Expose cached helpers depending on the deployment target."""
        if self.environment == "streamlit_cloud":
            # Streamlit Cloud friendly caching
            @st.cache_data(ttl=self.config["cache_ttl"], show_spinner=False)
            def cached_load_sales_data():
                from public_sheets_connector import PublicSheetsConnector
                connector = PublicSheetsConnector()
                return connector.load_data()

            @st.cache_data(ttl=300, show_spinner=False)
            def cached_process_ads_data(file_content, file_name):
                import pandas as pd
                import io

                if file_name.endswith('.csv'):
                    return pd.read_csv(io.StringIO(file_content))
                else:
                    return pd.read_excel(io.BytesIO(file_content))

            return cached_load_sales_data, cached_process_ads_data

        else:
            # Default caching for local/other deployments
            @st.cache_data(ttl=self.config["cache_ttl"])
            def cached_load_sales_data():
                from public_sheets_connector import PublicSheetsConnector
                connector = PublicSheetsConnector()
                return connector.load_data()
            
            @st.cache_data(ttl=300)
            def cached_process_ads_data(file_content, file_name):
                import pandas as pd
                import io
                
                if file_name.endswith('.csv'):
                    return pd.read_csv(io.StringIO(file_content))
                else:
                    return pd.read_excel(io.BytesIO(file_content))
            
            return cached_load_sales_data, cached_process_ads_data
    
    def get_secrets(self):
        """Return secrets depending on the provider."""
        secrets = {}

        if self.environment == "streamlit_cloud":
            try:
                if "google_sheets" in st.secrets:
                    secrets["google_sheets_url"] = st.secrets["google_sheets"]["url"]
                if "analytics" in st.secrets:
                    secrets["google_analytics"] = st.secrets["analytics"]["tracking_id"]
            except:
                pass

        elif self.environment == "heroku":
            secrets["google_sheets_url"] = os.environ.get("GOOGLE_SHEETS_URL")
            secrets["google_analytics"] = os.environ.get("GOOGLE_ANALYTICS_ID")

        elif self.environment in ["gcp", "aws"]:
            secrets["google_sheets_url"] = os.environ.get("GOOGLE_SHEETS_URL")
            secrets["google_analytics"] = os.environ.get("GOOGLE_ANALYTICS_ID")

        return secrets

    def setup_logging(self):
        """Configure logging with environment-aware defaults."""
        import logging

        log_level = getattr(logging, self.config["log_level"])

        # Formato do log
        if self.config["debug"]:
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            format_str = '%(levelname)s: %(message)s'
        
        logging.basicConfig(level=log_level, format=format_str)
        
        # Logger específico para a aplicação
        logger = logging.getLogger('ads_analyzer')
        logger.setLevel(log_level)
        
        return logger
    
    def get_error_tracking(self):
        """Return a callable that surfaces runtime errors appropriately."""
        if self.environment == "streamlit_cloud":
            def track_error(error, context=""):
                st.error(f"Error: {str(error)}")
                if self.config["debug"]:
                    st.exception(error)

            return track_error

        elif self.environment in ["heroku", "gcp", "aws"]:
            def track_error(error, context=""):
                import traceback
                error_details = {
                    "error": str(error),
                    "context": context,
                    "traceback": traceback.format_exc(),
                    "environment": self.environment
                }

                logger = logging.getLogger('ads_analyzer')
                logger.error(f"Error in {context}: {error}", extra=error_details)

                st.error("Something went wrong. Our team has been notified.")
                if self.config["debug"]:
                    st.exception(error)

            return track_error

        else:
            def track_error(error, context=""):
                st.error(f"Error in {context}: {str(error)}")
                st.exception(error)

            return track_error

    def optimize_for_environment(self):
        """Apply lightweight optimisations for different deployments."""
        optimizations = {
            "streamlit_cloud": {
                "pandas_optimization": True,
                "plotly_optimization": True,
                "memory_management": True
            },
            "heroku": {
                "pandas_optimization": True,
                "plotly_optimization": True,
                "memory_management": True,
                "cpu_optimization": True
            },
            "local": {
                "pandas_optimization": False,
                "plotly_optimization": False,
                "memory_management": False
            }
        }
        
        env_opts = optimizations.get(self.environment, optimizations["local"])
        
        if env_opts.get("pandas_optimization"):
            import pandas as pd
            pd.set_option('mode.chained_assignment', None)
            pd.set_option('display.max_columns', 20)

        if env_opts.get("plotly_optimization"):
            import plotly.io as pio
            pio.renderers.default = "browser" if self.environment == "local" else "plotly_mimetype+notebook"
        
        return env_opts


# .streamlit/config.toml template for Streamlit Cloud
STREAMLIT_CONFIG = """
[global]
developmentMode = false
showWarningOnDirectExecution = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 100

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
# text color remains unchanged in the template
textColor = "#262730"
"""

# secrets.toml template for Streamlit Cloud
SECRETS_TEMPLATE = """
# Template for secrets.toml on Streamlit Cloud

[google_sheets]
url = "https://docs.google.com/spreadsheets/d/1hVm1OALKQ244zuJBQV0SsQT08A2_JTDlPytUNULRofA/edit"

[analytics]
tracking_id = "GA_TRACKING_ID_HERE"

[database]
# Optional database settings
# host = "hostname"
# port = "5432"
# name = "database_name"
# user = "username"
# password = "password"
"""

# Dockerfile for container deployments
DOCKERFILE = """
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    software-properties-common \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Launch command
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""

# docker-compose.yml template for local development
DOCKER_COMPOSE = """
version: '3.8'

services:
  ads-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=docker
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    
  # Optional: Redis cache
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    
  # Optional: Postgres database
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=ads_analyzer
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
"""

# Production-oriented requirements template
REQUIREMENTS_PROD = """
# Core dependencies
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0

# Visualization
plotly>=5.15.0

# Google Sheets (público)
requests>=2.31.0

# Excel support
openpyxl>=3.1.0
xlsxwriter>=3.1.0

# Data processing
python-dateutil>=2.8.0

# Performance and monitoring
psutil>=5.9.0

# Optional: Analytics and ML
scikit-learn>=1.3.0
scipy>=1.11.0
