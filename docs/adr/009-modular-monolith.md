# ADR 009: Modular Monolith Initial Target Architecture

## Context
Over-engineering micro-services early introduces severe network overhead, deployment complexity, and distributed transaction pitfalls.

## Decision
Structure DateWithStranger as a **Modular Monolith** initially (`bot/`, `api/`, `workers/` sharing clean domain interfaces), designed for clear future service extraction.

## Alternatives Considered
- Distributed Microservices architecture: Excessive deployment overhead for current stage.

## Consequences
- Single codebase repository with decoupled domain packages. Simple local setup and operational clarity.

## Status
ACCEPTED
