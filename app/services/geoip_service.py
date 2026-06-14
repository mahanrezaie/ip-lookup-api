import ipaddress
from sqlalchemy.orm import Session
from geoip2.database import Reader

from app.models import IPLookup


def validate_ip(ip: str) -> str:
    return str(ipaddress.ip_address(ip))


def get_from_db(db: Session, ip: str):
    return (
        db.query(IPLookup)
        .filter(IPLookup.ip_address == ip)
        .first()
    )


def lookup_ip(ip: str, reader: Reader):
    try:
        res = reader.country(ip)
        return {
            "country_code": res.country.iso_code,
            "country_name": res.country.name
        }
    except Exception:
        return {
            "country_code": "XX",
            "country_name": "Unknown"
        }


def save(db: Session, ip: str, country: dict):
    record = IPLookup(
        ip_address=ip,
        country_code=country["country_code"],
        country_name=country["country_name"]
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
