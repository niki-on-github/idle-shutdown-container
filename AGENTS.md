# AGENTS.md for Idle Shutdown Container

## Build, Lint, and Test Commands

### Running the Application
```bash
# Run with default settings (INTERVAL_SECONDS=10, IDLE_TIME_SECONDS=500)
python3 main.py

# Run with custom environment variables
INTERVAL_SECONDS=30 IDLE_TIME_SECONDS=600 ENABLE_IDLE_DETECTION=false python3 main.py

# Run with API only (no automatic shutdown)
ENABLE_IDLE_DETECTION=false python3 main.py
```

### Testing
```bash
# Test single CPU monitoring function
python3 -c "from main import get_cpu_usage; print(get_cpu_usage())"

# Test single GPU monitoring function
python3 -c "from main import get_gpu_usage; print(get_gpu_usage())"

# Test environment variable parsing
python3 -c "from main import get_int_env; print(get_int_env('INTERVAL_SECONDS', 10))"
```

### Docker
```bash
# Build Docker image
docker build -t idle-shutdown-monitor .

# Run Docker container
docker run --privileged --device=/dev/nvidia0 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -e INTERVAL_SECONDS=10 \
  -e IDLE_TIME_SECONDS=500 \
  -v /host:/host \
  idle-shutdown-monitor

# Run with API only mode
docker run --privileged --device=/dev/nvidia0 \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=all \
  -e INTERVAL_SECONDS=10 \
  -e IDLE_TIME_SECONDS=500 \
  -e ENABLE_IDLE_DETECTION=false \
  -v /host:/host \
  idle-shutdown-monitor
```

## Code Style Guidelines

### Import Organization
- Group imports by source: stdlib → third-party → local
- Use import grouping with blank lines
- Suppress warnings selectively (`urllib3.disable_warnings()`)

### Function and Variable Naming
- Use descriptive, lowercase names with underscores for variables and functions
- Use `snake_case` for all Python identifiers
- Use uppercase for environment variable names
- Type hint all function signatures and variables

### Code Structure
- Keep functions single-responsibility (one clear task)
- Include docstrings for module-level descriptions
- Use simple `if __name__ == "__main__":` pattern for entry point
- Keep main logic at module level after imports

### Error Handling
- Wrap potentially failing operations in try/except blocks
- Print error messages and return safe defaults on failure
- Suppress SSL warnings when needed (requests with verify=False)
- Handle missing GPU drivers gracefully

### Logging
- Use `print()` statements for runtime information
- Format strings with f-strings for readability
- Include current state in debug output

### Type Hints
- Always specify return types for functions
- Specify parameter types when clear
- Use `bool`, `int`, `str` for basic types
- Use lists for multi-value returns

### Code Organization
- Place helper functions before main execution block
- Keep configuration logic near top of file
- Group related functionality together
- Minimize dependencies (only use required packages)
