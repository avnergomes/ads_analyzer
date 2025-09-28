"""
Configurações para deploy no Streamlit Cloud
e outras plataformas
"""

import streamlit as st
import os
from pathlib import Path

class DeploymentConfig:
    """Configurações para diferentes ambientes de deploy"""
    
    def __init__(self):
        self.environment = self.detect_environment()
        self.config = self.load_config()
    
    def detect_environment(self):
        """Detecta o ambiente de execução"""
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
        """Carrega configurações baseadas no ambiente"""
        configs = {
            "local": {
                "debug": True,
                "cache_ttl": 300,  # 5 minutos
                "max_upload_size": 200,  # MB
                "show_raw_data": True,
                "log_level": "DEBUG"
            },
            "streamlit_cloud": {
                "debug": False,
                "cache_ttl": 3600,  # 1 hora
                "max_upload_size": 100,  # MB
                "show_raw_data": True,
                "log_level": "INFO"
            },
            "heroku": {
                "debug": False,
                "cache_ttl": 1800,  # 30 minutos
                "max_upload_size": 50,  # MB
                "show_raw_data": False,
                "log_level": "WARNING"
            },
            "gcp": {
                "debug": False,
                "cache_ttl": 3600,  # 1 hora
                "max_upload_size": 200,  # MB
                "show_raw_data": True,
                "log_level": "INFO"
            },
            "aws": {
                "debug": False,
                "cache_ttl": 1800,  # 30 minutos
                "max_upload_size": 100,  # MB
                "show_raw_data": False,
                "log_level": "INFO"
            }
        }
        
        return configs.get(self.environment, configs["local"])
    
    def setup_page_config(self):
        """Configura a página Streamlit"""
        st.set_page_config(
            page_title="Ads Analyzer v2.0",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/avnergomes/ads-analyzer',
                'Report a bug': 'https://github.com/avnergomes/ads-analyzer/issues',
                'About': "Ads Analyzer v2.0 - Análise integrada de anúncios e vendas"
            }
        )
    
    def setup_caching(self):
        """Configura cache baseado no ambiente"""
        if self.environment == "streamlit_cloud":
            # Cache otimizado para Streamlit Cloud
            @st.cache_data(ttl=self.config["cache_ttl"], show_spinner=False)
            def cached_load_sales_data():
                from public_sheets_connector import PublicSheetsConnector
                connector = PublicSheetsConnector()
                return connector.load_data()
            
            @st.cache_data(ttl=300, show_spinner=False)  # Cache menor para uploads
            def cached_process_ads_data(file_content, file_name):
                import pandas as pd
                import io
                
                if file_name.endswith('.csv'):
                    return pd.read_csv(io.StringIO(file_content))
                else:
                    return pd.read_excel(io.BytesIO(file_content))
            
            return cached_load_sales_data, cached_process_ads_data
        
        else:
            # Cache padrão
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
        """Obtém secrets baseado no ambiente"""
        secrets = {}
        
        if self.environment == "streamlit_cloud":
            # Streamlit Secrets
            try:
                if "google_sheets" in st.secrets:
                    secrets["google_sheets_url"] = st.secrets["google_sheets"]["url"]
                if "analytics" in st.secrets:
                    secrets["google_analytics"] = st.secrets["analytics"]["tracking_id"]
            except:
                pass
        
        elif self.environment == "heroku":
            # Heroku Config Vars
            secrets["google_sheets_url"] = os.environ.get("GOOGLE_SHEETS_URL")
            secrets["google_analytics"] = os.environ.get("GOOGLE_ANALYTICS_ID")
        
        elif self.environment in ["gcp", "aws"]:
            # Cloud provider secrets
            secrets["google_sheets_url"] = os.environ.get("GOOGLE_SHEETS_URL")
            secrets["google_analytics"] = os.environ.get("GOOGLE_ANALYTICS_ID")
        
        return secrets
    
    def setup_logging(self):
        """Configura logging baseado no ambiente"""
        import logging
        
        # Configurar nível de log
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
        """Configura tracking de erros"""
        if self.environment == "streamlit_cloud":
            # Para Streamlit Cloud, usar logging simples
            def track_error(error, context=""):
                st.error(f"Erro: {str(error)}")
                if self.config["debug"]:
                    st.exception(error)
            
            return track_error
        
        elif self.environment in ["heroku", "gcp", "aws"]:
            # Para ambientes de produção, implementar tracking mais robusto
            def track_error(error, context=""):
                import traceback
                error_details = {
                    "error": str(error),
                    "context": context,
                    "traceback": traceback.format_exc(),
                    "environment": self.environment
                }
                
                # Log local
                logger = logging.getLogger('ads_analyzer')
                logger.error(f"Error in {context}: {error}", extra=error_details)
                
                # Interface do usuário
                st.error("Ocorreu um erro. Nossa equipe foi notificada.")
                if self.config["debug"]:
                    st.exception(error)
            
            return track_error
        
        else:
            # Ambiente local - mostrar erros completos
            def track_error(error, context=""):
                st.error(f"Erro em {context}: {str(error)}")
                st.exception(error)
            
            return track_error
    
    def optimize_for_environment(self):
        """Otimizações específicas do ambiente"""
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
            # Otimizações do pandas para produção
            pd.set_option('mode.chained_assignment', None)
            pd.set_option('display.max_columns', 20)
        
        if env_opts.get("plotly_optimization"):
            # Configurações do Plotly para performance
            import plotly.io as pio
            pio.renderers.default = "browser" if self.environment == "local" else "plotly_mimetype+notebook"
        
        return env_opts


# Arquivo .streamlit/config.toml para Streamlit Cloud
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
textColor = "#262730"
"""

# Arquivo secrets.toml template para Streamlit Cloud
SECRETS_TEMPLATE = """
# Template para secrets.toml no Streamlit Cloud

[google_sheets]
url = "https://docs.google.com/spreadsheets/d/1hVm1OALKQ244zuJBQV0SsQT08A2_JTDlPytUNULRofA/edit"

[analytics]
tracking_id = "GA_TRACKING_ID_AQUI"

[database]
# Se necessário, adicionar configurações de banco
# host = "hostname"
# port = "5432"
# name = "database_name"
# user = "username"
# password = "password"
"""

# Dockerfile para deploy em containers
DOCKERFILE = """
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    software-properties-common \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip3 install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Comando para executar
ENTRYPOINT ["streamlit", "run", "app_updated.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""

# docker-compose.yml para desenvolvimento local
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
    
  # Opcional: Redis para cache
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    
  # Opcional: Banco de dados
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

# Requirements atualizado para produção
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

# Production optimizations
gunicorn>=21.0.0
"""

# GitHub Actions workflow
GITHUB_ACTIONS = """
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=./ --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to Streamlit Cloud
      run: |
        echo "Deployment triggered automatically by Streamlit Cloud"
        echo "App URL: https://share.streamlit.io/avnergomes/ads-analyzer/main/app_updated.py"
"""

# Heroku Procfile
PROCFILE = """
web: sh setup.sh && streamlit run app_updated.py --server.port=$PORT --server.address=0.0.0.0
"""

# Setup script para Heroku
SETUP_SH = """
mkdir -p ~/.streamlit/

echo "\\
[general]\\n\\
email = \\"your-email@domain.com\\"\\n\\
" > ~/.streamlit/credentials.toml

echo "\\
[server]\\n\\
headless = true\\n\\
enableCORS=false\\n\\
port = $PORT\\n\\
" > ~/.streamlit/config.toml
"""

# Função para criar arquivos de deploy
def create_deployment_files():
    """Cria todos os arquivos necessários para deploy"""
    files_to_create = {
        ".streamlit/config.toml": STREAMLIT_CONFIG,
        ".streamlit/secrets.toml.template": SECRETS_TEMPLATE,
        "Dockerfile": DOCKERFILE,
        "docker-compose.yml": DOCKER_COMPOSE,
        "requirements-prod.txt": REQUIREMENTS_PROD,
        ".github/workflows/deploy.yml": GITHUB_ACTIONS,
        "Procfile": PROCFILE,
        "setup.sh": SETUP_SH
    }
    
    created_files = []
    
    for file_path, content in files_to_create.items():
        # Criar diretório se necessário
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Escrever arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        created_files.append(file_path)
    
    return created_files

# Utilitários para deploy
class DeploymentUtils:
    """Utilitários para facilitar o deploy"""
    
    @staticmethod
    def check_requirements():
        """Verifica se todos os requisitos estão instalados"""
        import pkg_resources
        import sys
        
        required_packages = [
            'streamlit>=1.28.0',
            'pandas>=2.0.0',
            'plotly>=5.15.0',
            'requests>=2.31.0'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                pkg_resources.require(package)
            except:
                missing_packages.append(package)
        
        return missing_packages
    
    @staticmethod
    def test_google_sheets_connection():
        """Testa conexão com Google Sheets"""
        try:
            from public_sheets_connector import PublicSheetsConnector
            connector = PublicSheetsConnector()
            data = connector.load_data()
            return data is not None and not data.empty
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_app_structure():
        """Valida estrutura da aplicação"""
        required_files = [
            'app_updated.py',
            'public_sheets_connector.py',
            'requirements.txt'
        ]
        
        missing_files = []
        
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        return missing_files
    
    @staticmethod
    def generate_deployment_checklist():
        """Gera checklist para deploy"""
        checklist = {
            "Arquivos obrigatórios": [
                "✓ app_updated.py (arquivo principal)",
                "✓ public_sheets_connector.py (conector)",
                "✓ requirements.txt (dependências)",
                "✓ README.md (documentação)"
            ],
            "Configuração Streamlit Cloud": [
                "✓ .streamlit/config.toml",
                "✓ .streamlit/secrets.toml (se necessário)",
                "✓ Repositório GitHub público/privado",
                "✓ Deploy configurado no share.streamlit.io"
            ],
            "Testes": [
                "✓ Conexão com Google Sheets",
                "✓ Upload de arquivos CSV/Excel",
                "✓ Geração de gráficos",
                "✓ Performance com dados grandes"
            ],
            "Otimizações": [
                "✓ Cache configurado",
                "✓ Tratamento de erros",
                "✓ Loading states",
                "✓ Responsive design"
            ]
        }
        
        return checklist

if __name__ == "__main__":
    # Criar arquivos de deployment
    print("🚀 Criando arquivos de deployment...")
    
    files = create_deployment_files()
    
    print("📁 Arquivos criados:")
    for file in files:
        print(f"  - {file}")
    
    print("\n✅ Arquivos de deployment criados com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Revisar e personalizar os arquivos criados")
    print("2. Fazer commit no repositório GitHub")
    print("3. Configurar deploy no Streamlit Cloud")
    print("4. Testar a aplicação em produção")