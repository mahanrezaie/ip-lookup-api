from fastapi import FastAPI, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from geoip2.database import Reader
import time

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.database import SessionLocal, engine, Base, check_db
from app.schemas import CountryResponse
from app.services.geoip_service import (
    validate_ip,
    get_from_db,
    lookup_ip,
    save
)

from app.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS
)

# -------------------------
# App
# -------------------------
app = FastAPI(title="IP Country Service")


# -------------------------
# Startup
# -------------------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# -------------------------
# DB dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# GeoIP dependency
# -------------------------
def get_reader():
    return Reader("geoip/GeoLite2-Country.mmdb")


# -------------------------
# Metrics middleware
# -------------------------
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start

    endpoint = request.url.path
    method = request.method
    status = response.status_code

    HTTP_REQUESTS_TOTAL.labels(
        method=method,
        endpoint=endpoint,
        status=status
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        endpoint=endpoint
    ).observe(duration)

    return response


# -------------------------
# Health: live
# -------------------------
@app.get("/health/live")
def live():
    return {"status": "alive"}


# -------------------------
# Health: ready
# -------------------------
@app.get("/health/ready")
def ready(response: Response):
    if not check_db():
        response.status_code = 503
        return {"status": "not ready", "db": "down"}

    return {"status": "ready", "db": "up"}


# -------------------------
# Metrics endpoint
# -------------------------
@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# -------------------------
# Main endpoint
# -------------------------
@app.get("/country/{ip}", response_model=CountryResponse)
def get_country(
    ip: str,
    db: Session = Depends(get_db),
    reader: Reader = Depends(get_reader)
):

    try:
        ip = validate_ip(ip)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid IP address")

    record = get_from_db(db, ip)

    if record:
        return {
            "ip": record.ip_address,
            "country_code": record.country_code,
            "country_name": record.country_name,
            "cached": True
        }

    country = lookup_ip(ip, reader)

    record = save(db, ip, country)

    return {
        "ip": record.ip_address,
        "country_code": record.country_code,
        "country_name": record.country_name,
        "cached": False
    }
