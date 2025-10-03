# Ads Analyzer

Integrated Streamlit dashboard that combines Meta advertising exports with live ticket sales pulled from a public Google Sheet. The app normalises the data, calculates funnel metrics, and surfaces insights for individual shows.

## Key features
- Automatic parsing of the public ticket sales sheet until the `endRow` marker to avoid historical noise.
- Currency-aware revenue handling that converts non-USD ticket revenue into USD using live exchange rates (with sensible fallbacks when the API is unavailable).
- Snapshot-aware ticket metrics so capacity, tickets sold, revenue, and occupancy reflect the latest report for every show.
- Integrated ad and sales analysis tabs with funnel summaries, pacing alerts, and downloadable raw datasets.

## Local development
1. Create a virtual environment and install the dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Upload the three Meta reports (Days, Days + Placement + Device, Days + Time) when prompted in the sidebar. The ticket sales sheet loads automatically on start-up.

## Deploying on an Ubuntu 20.04 VPS
1. Install system dependencies and Python:
   ```bash
   sudo apt update && sudo apt install -y python3 python3-venv python3-pip
   ```
2. Clone the repository (or copy the project files) to the server and move into the folder.
3. Create the virtual environment and install requirements as shown in the local instructions above.
4. Launch the app bound to the public interface:
   ```bash
   streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   ```
5. (Optional) Use a process manager such as `systemd`, `supervisor`, or `tmux` to keep the app running in the background. Reverse proxying through Nginx with TLS is recommended for production use.

## Deploying on Fly.io
1. Install the Fly CLI (`curl -L https://fly.io/install.sh | sh`) and log in with `fly auth login`.
2. Inside the project directory, create a `fly.toml` by running `fly launch --no-deploy`. Choose a Python builder when prompted or set the following buildpack in `fly.toml`:
   ```toml
   [build]
   builder = "paketobuildpacks/builder:base"
   buildpacks = ["gcr.io/paketo-buildpacks/python"]
   ```
3. Add the startup command to the `fly.toml` file:
   ```toml
   [processes]
   app = "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
   ```
4. Deploy with `fly deploy`. Fly.io automatically sets the `PORT` environment variable that Streamlit reads from the process definition.

## Configuration notes
- Exchange rates are refreshed every six hours using [open.er-api.com](https://open.er-api.com). If the request fails, the app falls back to sensible static rates so revenue metrics remain available offline.
- The `public_sheets_connector.py` module exposes `PublicSheetsConnector.get_data_summary` for quick health checks and already returns values that reflect the latest entry per show.
- For alternative deployments (Heroku, AWS, etc.) refer to `deployment_config.py`, which contains environment-aware caching and logging helpers.
