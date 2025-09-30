# 🚀 Guia de Deployment - Ads Analyzer v2.0

Este guia cobre diferentes opções de deployment para o Ads Analyzer.

## 📋 Pré-requisitos

Antes de fazer o deploy, certifique-se de que:

- [ ] A aplicação funciona localmente
- [ ] Todos os testes passaram (`python test_installation.py`)
- [ ] Os arquivos sensíveis estão no `.gitignore`
- [ ] As dependências estão documentadas em `requirements.txt`

## 🌐 Streamlit Cloud (Recomendado)

### Vantagens
- ✅ Gratuito para projetos públicos
- ✅ Deploy automático via GitHub
- ✅ SSL/HTTPS incluído
- ✅ Fácil gerenciamento de secrets

### Passos

1. **Prepare o Repositório**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Acesse Streamlit Cloud**
   - Vá para [share.streamlit.io](https://share.streamlit.io)
   - Faça login com sua conta GitHub
   - Clique em "New app"

3. **Configure a Aplicação**
   - Repository: `avnergomes/ads_analyzer`
   - Branch: `main`
   - Main file path: `v2/app.py`

4. **Configure Secrets** (se necessário)
   - Clique em "Advanced settings"
   - Cole o conteúdo do `secrets.toml.example`
   - Preencha com seus valores reais

5. **Deploy**
   - Clique em "Deploy!"
   - Aguarde alguns minutos

### Atualizações
O deploy é automático a cada push para o repositório.

---

## 🐳 Docker

### Dockerfile

Crie um `Dockerfile` na pasta `v2`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expor porta
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando de inicialização
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build e Run

```bash
# Build
docker build -t ads-analyzer:v2 .

# Run
docker run -p 8501:8501 ads-analyzer:v2

# Run com volume para dados
docker run -p 8501:8501 -v $(pwd)/data:/app/data ads-analyzer:v2
```

### Docker Compose

Crie `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ads-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=8501
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Execute com:
```bash
docker-compose up -d
```

---

## ☁️ Heroku

### Preparação

1. **Criar arquivos necessários**

`Procfile`:
```
web: streamlit run v2/app.py --server.port=$PORT --server.address=0.0.0.0
```

`runtime.txt`:
```
python-3.10.12
```

`setup.sh`:
```bash
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"seu@email.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

2. **Deploy**

```bash
# Login no Heroku
heroku login

# Criar app
heroku create seu-app-name

# Deploy
git push heroku main

# Abrir app
heroku open
```

### Configurar Secrets

```bash
heroku config:set GOOGLE_SHEETS_URL="sua_url_aqui"
```

---

## 🔧 VPS (DigitalOcean, AWS, etc.)

### 1. Configurar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3-pip python3-venv nginx -y

# Criar usuário
sudo useradd -m -s /bin/bash streamlit
sudo su - streamlit
```

### 2. Configurar Aplicação

```bash
# Clone o repositório
git clone https://github.com/avnergomes/ads_analyzer.git
cd ads_analyzer/v2

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Criar Serviço Systemd

Crie `/etc/systemd/system/ads-analyzer.service`:

```ini
[Unit]
Description=Ads Analyzer Streamlit App
After=network.target

[Service]
Type=simple
User=streamlit
WorkingDirectory=/home/streamlit/ads_analyzer/v2
Environment="PATH=/home/streamlit/ads_analyzer/v2/venv/bin"
ExecStart=/home/streamlit/ads_analyzer/v2/venv/bin/streamlit run app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Iniciar Serviço

```bash
sudo systemctl daemon-reload
sudo systemctl enable ads-analyzer
sudo systemctl start ads-analyzer
sudo systemctl status ads-analyzer
```

### 5. Configurar Nginx (opcional)

Crie `/etc/nginx/sites-available/ads-analyzer`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ativar:
```bash
sudo ln -s /etc/nginx/sites-available/ads-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL com Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com
```

---

## 🔒 Segurança

### Variáveis de Ambiente

Nunca comite secrets no código. Use:

**Local Development:**
```bash
# .env
GOOGLE_SHEETS_URL=sua_url
```

**Streamlit Cloud:**
- Use o painel de Secrets

**Heroku:**
```bash
heroku config:set CHAVE=valor
```

**VPS:**
```bash
export GOOGLE_SHEETS_URL=sua_url
```

### Checklist de Segurança

- [ ] Secrets não estão no código
- [ ] `.gitignore` está configurado
- [ ] HTTPS está habilitado
- [ ] Firewall está configurado (VPS)
- [ ] Atualizações automáticas habilitadas
- [ ] Backups configurados
- [ ] Logs monitorados

---

## 📊 Monitoramento

### Logs

**Streamlit Cloud:**
- Veja logs no dashboard

**Heroku:**
```bash
heroku logs --tail
```

**VPS:**
```bash
sudo journalctl -u ads-analyzer -f
```

### Uptime Monitoring

Use serviços como:
- [UptimeRobot](https://uptimerobot.com) (gratuito)
- [Pingdom](https://pingdom.com)
- [StatusCake](https://statuscake.com)

---

## 🔄 CI/CD

### GitHub Actions

Crie `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]
    paths:
      - 'v2/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd v2
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd v2
          python test_installation.py
```

---

## 💰 Custos Estimados

| Plataforma | Custo Mensal | Recursos |
|------------|--------------|----------|
| Streamlit Cloud | $0 - $250 | Gratuito (limitado) até Business |
| Heroku | $0 - $25 | Free até Hobby |
| DigitalOcean | $5 - $20 | Droplet básico |
| AWS | $10 - $50 | EC2 t3.micro |
| Render | $0 - $25 | Free até Individual |

---

## 🆘 Troubleshooting de Deploy

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt --upgrade
```

### Erro: "Port already in use"
```bash
# Mudar porta
streamlit run app.py --server.port=8502
```

### Erro: "Memory exceeded"
- Reduzir tamanho dos arquivos
- Aumentar limite de memória
- Otimizar código

### App está lento
- Adicionar caching (`@st.cache_data`)
- Reduzir processamento desnecessário
- Usar servidor mais potente

---

## 📚 Recursos Adicionais

- [Documentação Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Docker Docs](https://docs.docker.com)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)

---

**Última atualização:** Setembro 2025
