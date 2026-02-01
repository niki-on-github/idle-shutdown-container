# Idle Shutdown Container

System monitoring container for AI clusters that monitors CPU, GPU, and SSH sessions, then powers down when idle.

## Features

- Real-time CPU and GPU usage monitoring
- SSH session monitoring
- Configurable idle thresholds
- REST API for shutdown control (requires API_USERNAME and API_PASSWORD to be set)
- Docker container with NVIDIA GPU support

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_PORT` | 8000 | Port for REST API server |
| `API_USERNAME` | admin | Username for `/poweroff` endpoint (required for API) |
| `API_PASSWORD` | shutdown123 | Password for `/poweroff` endpoint (required for API) |
| `INTERVAL_SECONDS` | 10 | Monitoring interval |
| `IDLE_TIME_SECONDS` | 500 | Idle time before shutdown |
| `CPU_IDLE_THRESHOLD_PERCENT` | 20 | CPU usage below which is considered idle |
| `GPU_IDLE_THRESHOLD_PERCENT` | 5 | GPU usage below which is considered idle |
| `SURPLUS_CHECK_URL` | | Optional URL to check for surplus capacity |
| `ENABLE_IDLE_DETECTION` | false | Enable/disable automatic idle detection |

## Installation & Setup

### Clone and Install

```bash
git clone <repository-url>
cd idle-shutdown-container
```

### Docker (Recommended)

```bash
# Build Docker image
docker build -t idle-shutdown-monitor .

# Run container
docker run --privileged --device=/dev/nvidia0 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -e INTERVAL_SECONDS=10 \
  -e IDLE_TIME_SECONDS=500 \
  -v /host:/host \
  -p 8000:8000 \
  idle-shutdown-monitor
```

### Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default settings
python3 main.py

# Run with custom settings
INTERVAL_SECONDS=30 IDLE_TIME_SECONDS=600 ENABLE_IDLE_DETECTION=false python3 main.py

# API only mode (no automatic shutdown)
ENABLE_IDLE_DETECTION=false python3 main.py
```

## REST API

The container includes a FastAPI-based REST API for controlling the shutdown sequence. The API is only enabled when both `API_USERNAME` and `API_PASSWORD` environment variables are set. `/health` endpoint is always available if API is running.

### API Health Check

```bash
# When API is enabled
curl http://localhost:8000/health

# When API is disabled (no credentials set)
curl http://localhost:8000/health
# Returns: Connection refused or similar
```

**Response (when API enabled):** `{"status": "healthy"}`

### Trigger Poweroff

```bash
# When API is enabled
curl -u admin:shutdown123 -X POST http://localhost:8000/poweroff

# When API is disabled (credentials not set)
curl -u admin:shutdown123 -X POST http://localhost:8000/poweroff
# Returns: {"error": "API credentials not configured"}, 503

# Invalid credentials
curl -u wrong:password -X POST http://localhost:8000/poweroff
# Returns: {"error": "Invalid credentials"}, 401
```

**Response (when API enabled):** `{"message": "Shutdown initiated"}`

**Behavior:**
1. API returns `200 OK` immediately
2. Monitoring loop receives shutdown signal
3. System waits 5 seconds
4. Executes poweroff

### Toggle Idle Detection

To disable automatic idle detection and run with API only, set `ENABLE_IDLE_DETECTION=false`:

```bash
ENABLE_IDLE_DETECTION=false python3 main.py
```

This allows you to manually control shutdown via the API only.

## Monitoring

### Check CPU Usage

```bash
python3 -c "from main import get_cpu_usage; print(get_cpu_usage())"
```

### Check GPU Usage

```bash
python3 -c "from main import get_gpu_usage; print(get_gpu_usage())"
```

### Test Environment Variables

```bash
python3 -c "from main import get_int_env; print(get_int_env('INTERVAL_SECONDS', 10))"
```

## How It Works

1. **API Server**: Runs on configured port in background thread, always available
2. **Monitoring Loop**: Runs every `INTERVAL_SECONDS`, checks CPU and GPU usage
3. **Idle Detection**: If both CPU and GPU are below their thresholds
4. **Idle Timer**: Counts consecutive idle periods, waits for `IDLE_TIME_SECONDS`
5. **Shutdown**: When timer reaches limit, executes system poweroff
6. **API Control**: Provides endpoint to trigger shutdown immediately with confirmation delay
7. **Idle Detection Toggle**: Controlled via `ENABLE_IDLE_DETECTION` environment variable

## Project Structure

```
.
├── AGENTS.md           # Development guidelines
├── Dockerfile          # Docker image definition
├── main.py             # Main application (monitoring + API)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # This file
```

## Security Notes

- API uses Basic Authentication (plaintext over HTTPS recommended)
- Default credentials should be changed for production
- API port can be customized via `API_PORT`
- Consider using reverse proxy with SSL for production deployments

## License

MIT License
