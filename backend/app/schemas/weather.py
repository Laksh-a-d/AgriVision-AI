from typing import Optional
from pydantic import BaseModel, Field


class WeatherData(BaseModel):
    """
    Structured agro-climatic and weather payload for an Indian State and District.
    """
    state: str = Field(..., description="Indian State / Union Territory name", json_schema_extra={"example": "Maharashtra"})
    district: str = Field(..., description="District name", json_schema_extra={"example": "Nagpur"})
    location_name: str = Field(..., description="Full resolved location name", json_schema_extra={"example": "Nagpur, Maharashtra, India"})
    latitude: float = Field(..., description="Geographic latitude coordinate", json_schema_extra={"example": 21.1458})
    longitude: float = Field(..., description="Geographic longitude coordinate", json_schema_extra={"example": 79.0882})
    temperature: float = Field(..., description="Current ambient temperature in Celsius (°C)", json_schema_extra={"example": 28.5})
    humidity: float = Field(..., description="Current relative humidity percentage (%)", json_schema_extra={"example": 62.0})
    annual_rainfall: float = Field(..., description="Normal annual precipitation in mm (IMD Long Period Average)", json_schema_extra={"example": 1050.0})
    rainfall: float = Field(..., description="Agriculturally relevant rainfall in mm for crop cycle recommendation", json_schema_extra={"example": 185.0})
    weather_condition: Optional[str] = Field(None, description="Current meteorological condition description", json_schema_extra={"example": "Clear sky"})
    source: str = Field("Open-Meteo & IMD Climate Normals", description="Data provenance sources")
    fetched_at: str = Field(..., description="ISO 8601 timestamp of data retrieval")
