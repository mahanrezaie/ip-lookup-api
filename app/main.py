from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base, check_db
from app.schemas import CountryResponse
from app.services.geoip_service import (
    validate_ip,
    get_from_db,
    lookup_ip,
    save
)
from geoip2.database import Reader

# create tables (simple approach for interview)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IP Country Service")


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
# LIVENESS (process health only)
# -------------------------
@app.get("/health/live")
def live():
    return {"status": "alive"}


# -------------------------
# READINESS (DB-aware)
# -------------------------
@app.get("/health/ready")
def ready(response: Response):
    if not check_db():
        response.status_code = 503
        return {"status": "not ready", "db": "down"}

    return {"status": "ready", "db": "up"}

# -------------------------
# Main endpoint
# -------------------------
@app.get("/country/{ip}", response_model=CountryResponse)
def get_country(
    ip: str,
    db: Session = Depends(get_db),
    reader: Reader = Depends(get_reader)
):

    # 1. validate IP
    try:
        ip = validate_ip(ip)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid IP address")

    # 2. check cache (DB)
    record = get_from_db(db, ip)

    if record:
        return {
            "ip": record.ip_address,
            "country_code": record.country_code,
            "country_name": record.country_name,
            "cached": True
        }

    # 3. lookup GeoIP
    country = lookup_ip(ip, reader)

    # 4. save to DB
    record = save(db, ip, country)

    # 5. return response
    return {
        "ip": record.ip_address,
        "country_code": record.country_code,
        "country_name": record.country_name,
        "cached": False
    }
