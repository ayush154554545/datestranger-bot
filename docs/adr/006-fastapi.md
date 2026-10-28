# ADR 006: FastAPI for Backend API Micro-services

## Context
A structured API layer is required for health checks, administrative dashboards, media upload signing, and web client interactions.

## Decision
Adopt **FastAPI** (Python 3.11 + Pydantic v2) for `api/`.

## Alternatives Considered
- Flask: Lacks native async request handling and automatic OpenAPI documentation.
- Django REST Framework: Overweight for high-speed micro-services.

## Consequences
- High-performance async endpoint execution.
- Auto-generated OpenAPI (Swagger) documentation and typed Pydantic request validation.

## Status
ACCEPTED
