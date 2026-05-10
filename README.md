# EVLease

A modern EV leasing platform built as a GraphQL federation microservices architecture, inspired by [Octopus EV](https://octopusev.com/).

## Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — async Python web framework for each microservice
- **[Ariadne](https://ariadnegraphql.org/)** — schema-first GraphQL library
- **[ariadne-federation](https://github.com/mirumee/ariadne-starlette)** — GraphQL Federation support for Ariadne subgraphs
- **[UV](https://docs.astral.sh/uv/)** — fast Python package and project manager
- **[Ruff](https://docs.astral.sh/ruff/)** — fast Python linter and formatter

### Gateway
- **[Apollo Router](https://www.apollographql.com/docs/router/)** — Rust-based GraphQL federation gateway

### Frontend
- **[Next.js](https://nextjs.org/)** — React framework with App Router
- **[Apollo Client](https://www.apollographql.com/docs/react/)** — GraphQL client

### Infrastructure
- **Docker + Docker Compose** — local development orchestration
- **PostgreSQL** — one database per service

---

## Architecture

```
NextJS Frontend
      │
      ▼
Apollo Router (Gateway)        ← Federation supergraph
      │
  ┌───┼──────────────────┐
  ▼   ▼                  ▼
Vehicles  Leasing   Customers  Orders
Service   Service   Service    Service
  │         │           │         │
  ▼         ▼           ▼         ▼
Postgres  Postgres  Postgres  Postgres
```

Each backend service is an independent FastAPI application exposing a GraphQL Federation subgraph. The Apollo Router composes all subgraph schemas into a single unified supergraph that the frontend queries.

---

## Services

| Service | Port | Responsibility |
|---|---|---|
| `vehicles-service` | `8001` | Vehicle catalog, specs, images, availability |
| `leasing-service` | `8002` | Quote engine, pricing rules, lease terms |
| `customers-service` | `8003` | Auth, user profiles, documents |
| `orders-service` | `8004` | Applications, order status, fulfillment |
| Gateway | `4000` | Apollo Router — unified GraphQL API |
| Frontend | `3000` | Next.js application |

---

## Repository Structure

```
evlease/
├── gateway/                  # Apollo Router configuration
│   ├── router.yaml
│   └── supergraph.yaml
├── services/
│   ├── vehicles/             # FastAPI + Ariadne subgraph
│   │   ├── src/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   ├── leasing/
│   ├── customers/
│   └── orders/
├── frontend/                 # Next.js application
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites

- [UV](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Node.js](https://nodejs.org/) 20+

### Running Locally

```bash
# Start all services
docker compose up

# Or run a single service for development
cd services/vehicles
uv run fastapi dev src/main.py
```

---

## Development

### Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting, enforced via [pre-commit](https://pre-commit.com/) hooks.

```bash
# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .
```

### Testing

```bash
cd services/vehicles
uv run pytest
```

---

## GraphQL

The unified GraphQL playground is available at `http://localhost:4000` when the gateway is running.

Individual subgraph schemas can be explored at each service's `/graphql` endpoint during development.
