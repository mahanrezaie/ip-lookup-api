from pydantic import BaseModel


class CountryResponse(BaseModel):
    ip: str
    country_code: str
    country_name: str
    cached: bool

