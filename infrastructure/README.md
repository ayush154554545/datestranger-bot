# Infrastructure (`infrastructure/`)

Deployment manifests, Docker compose setups, and monitoring configurations for DateWithStranger.

## Subdirectories
- `infrastructure/docker/`: Dockerfiles and docker-compose files for local development (Redis, Postgres, API, Workers, Bot).
- `infrastructure/deployment/`: Production manifests for Render, Fly.io, Cloudflare.
- `infrastructure/monitoring/`: Grafana/Prometheus metrics configuration, health probes, log aggregators.
