# Aidbox Validator

A validation service built with Python and Aidbox for FHIR resource validation.

## Prerequisites

- Docker and Docker Compose
- Make
- Aidbox license key

## Quick Start

1. **Set up environment variables**
   ```bash
   cp env.tpl .env
   ```
   Edit `.env` and add your Aidbox license key:
   ```
   AIDBOX_LICENSE=your-license-key-here
   ```

2. **Start the application**
   ```bash
   make run
   ```
   This will pull images, build the validator app, and start all services.

3. **Access the services**
   - Aidbox: http://localhost:8080

## Available Commands

```bash
make pull   # Pull latest Docker images
make build  # Build the validator application
make up     # Start all services
make stop   # Stop running services
make down   # Stop and remove containers
make run    # Pull, build, and start (recommended)
```

## Architecture

The project consists of three main services:

- **validator-app**: Python application using Poetry and Gunicorn with aiohttp
- **devbox**: Aidbox instance for FHIR validation
- **devbox-db**: PostgreSQL database for Aidbox

## Development

For development setup and testing instructions, see [backend/README.md](backend/README.md).

## Project Structure

```
.
├── backend/          # Python validator application
├── resources/        # Aidbox configuration resources
├── env/              # Environment configuration files
├── compose.yaml      # Docker Compose configuration
├── Makefile          # Build and run commands
└── .env              # Environment variables (create from env.tpl)
```