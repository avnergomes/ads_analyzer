# 🚀 Deployment Guide – Ads Analyzer v2.0

This guide outlines options for hosting Ads Analyzer in production environments.

## ✅ Pre-deployment checklist
- Python 3.9 or later installed on the target server
- `pip install -r requirements.txt` completed without errors
- Environment variables or secrets ready for any external services you plan to integrate
- Port `8501` open if the app will be exposed publicly

## ☁️ Option 1: Streamlit Community Cloud
1. Push the repository to GitHub.
2. Create a new Streamlit app from the `v2/app.py` entry point.
3. Configure any secrets in the Streamlit dashboard (if required).
4. Set the Python version to 3.9+ in the advanced settings.

**Pros:** Fastest setup, automatic scaling.  
**Cons:** Limited resources, no custom domains on the free tier.

## 🐳 Option 2: Docker container
1. Create a `Dockerfile` similar to the snippet below:
   ```Dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt ./
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
   ```
2. Build and run locally:
   ```bash
   docker build -t ads-analyzer:v2 .
   docker run -p 8501:8501 ads-analyzer:v2
   ```
3. Deploy the image to your preferred container platform (Fly.io, AWS ECS, Google Cloud Run, etc.).

**Pros:** Consistent runtime, portable across environments.  
**Cons:** Requires container orchestration knowledge.

## 🖥 Option 3: Ubuntu VPS (e.g., DigitalOcean, Linode)
1. Provision an Ubuntu 20.04/22.04 server with at least 2 vCPUs and 4 GB RAM.
2. Install system dependencies:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv
   ```
3. Clone the repository and create a virtual environment:
   ```bash
   git clone https://github.com/avnergomes/ads_analyzer.git
   cd ads_analyzer/v2
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Run the app behind a process manager:
   ```bash
   nohup streamlit run app.py --server.address=0.0.0.0 --server.port=8501 &
   ```
5. (Optional) Configure Nginx as a reverse proxy to serve the app over HTTPS.

**Pros:** Full control over hardware and networking.  
**Cons:** Requires manual monitoring and patching.

## 🔐 Secrets management
- Store API keys or credentials in `.streamlit/secrets.toml` (and never commit the file).
- For Docker deployments, pass secrets through environment variables and template them into `secrets.toml` at runtime.
- Rotate credentials regularly and follow the principle of least privilege.

## 📈 Monitoring and maintenance
- Enable Streamlit logging (`streamlit run app.py --logger.level=info`) to capture usage metrics.
- Schedule regular backups of uploaded Meta exports if you persist them on disk.
- Update dependencies quarterly and rerun regression tests (`python -m py_compile v2/public_sheets_connector.py v2/app.py`).

## 🆘 Deployment troubleshooting
- **App fails to start:** Check the container or process logs for missing dependencies.
- **Port already in use:** Stop other services using port `8501` or configure a different port via `--server.port`.
- **Static files not loading behind a proxy:** Ensure `X-Forwarded-Proto` headers are preserved and disable CORS/XSRF protection only when necessary.

Following these guidelines will help you deploy Ads Analyzer securely and keep the dashboards available for stakeholders.
