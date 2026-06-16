# IP Country Service

A lightweight FastAPI service that resolves an IP address to its country using MaxMind GeoLite2 data, with optional caching in a database and Prometheus metrics for monitoring.

---

## What it does

- Takes an IP address and returns:
    - Country code
    - Country name
- Caches lookups in a database to avoid repeated GeoIP queries
- Exposes basic health checks
- Exposes Prometheus metrics for request tracking and latency

---

## Endpoints

### `GET /country/{ip}`

Returns country information for an IP.

Example response:

```
{  "ip": "8.8.8.8",  "country_code": "US",  "country_name": "United States",  "cached": true}
```

If the IP is not in the database, it will be resolved via GeoIP and stored.

---

### `GET /health/live`

Simple liveness check.

```
{ "status": "alive" }
```

---

### `GET /health/ready`

Checks if the service is ready to serve traffic (DB check included).

- `200 OK` → ready
- `503` → database not reachable

---

### `GET /metrics`

Prometheus metrics endpoint.

Includes:

- Request count per endpoint, method, status
- Request duration per endpoint

---

## Metrics

Two main metrics are exposed:

- `HTTP_REQUESTS_TOTAL`
    - Labels: `method`, `endpoint`, `status`
- `HTTP_REQUEST_DURATION_SECONDS`
    - Labels: `endpoint`

These are automatically recorded for every request via middleware.

---

## How caching works

1. Request comes in to `/country/{ip}`
2. IP is validated
3. Database is checked first
4. If found → return cached result
5. If not found → GeoIP lookup happens
6. Result is saved to DB and returned

---

## Project structure (expected)

```
app/
  database.py
  metrics.py
  schemas.py
  services/
    geoip_service.py
main.py
geoip/
  GeoLite2-Country.mmdb
```

---

## Running the service

Install dependencies:

```
pip install fastapi uvicorn sqlalchemy geoip2 prometheus_client
```

Start the server:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Notes

- DB tables are created automatically on startup
- Reader is initialized per request (can be optimized if needed)
- Designed to be simple and easy to extend (Redis cache, batching, etc.)
