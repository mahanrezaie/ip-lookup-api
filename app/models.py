from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.sql import func

from app.database import Base


class IPLookup(Base):
    __tablename__ = "ip_lookup"

    ip_address = Column(INET, primary_key=True, index=True)
    country_code = Column(String(2), nullable=False)
    country_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
