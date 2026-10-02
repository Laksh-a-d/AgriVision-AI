from typing import List, Literal, Optional, Any
from pydantic import BaseModel, Field, field_validator


class PriceForecastRequest(BaseModel):
    """
    Input request for Crop Market Price Forecasting.
    """
    commodity: str = Field("Onion", description="Target agricultural commodity name", json_schema_extra={"example": "Onion"})
    market: str = Field("Lasalgaon", description="Target APMC wholesale mandi market", json_schema_extra={"example": "Lasalgaon"})
    historical_prices: List[float] = Field(
        ...,
        min_length=30,
        description="Chronological historical daily modal prices (minimum 30 continuous observations)",
        json_schema_extra={"example": [1200.0 + i * 15 for i in range(30)]}
    )
    forecast_horizon: Literal[1, 7, 14, 30] = Field(
        7,
        description="Forecast horizon in days (supported: 1, 7, 14, 30)",
        json_schema_extra={"example": 7}
    )

    @field_validator("historical_prices")
    @classmethod
    def validate_prices(cls, v: List[float]) -> List[float]:
        if len(v) < 30:
            raise ValueError("historical_prices must contain at least 30 continuous daily observations.")
        for idx, p in enumerate(v):
            if p <= 0:
                raise ValueError(f"Historical price at index {idx} must be strictly positive (got {p}).")
        return v


class PriceForecastDayItem(BaseModel):
    """
    Daily price forecast item.
    """
    day: int = Field(..., description="Day index of the forecast horizon", json_schema_extra={"example": 1})
    predicted_modal_price: float = Field(..., description="Forecasted modal spot price in INR per Quintal", json_schema_extra={"example": 1638.93})
    forecasted_price: Optional[float] = Field(None, description="Forecasted price alias matching frontend contract", json_schema_extra={"example": 1638.93})
    unit: str = Field("INR/Quintal", description="Currency per weight unit", json_schema_extra={"example": "INR/Quintal"})

    def model_post_init(self, __context: Any) -> None:
        if self.forecasted_price is None:
            self.forecasted_price = self.predicted_modal_price


class PriceForecastResponse(BaseModel):
    """
    Price forecast result payload.
    """
    commodity: str = Field(..., json_schema_extra={"example": "Onion"})
    market: str = Field(..., json_schema_extra={"example": "Lasalgaon"})
    forecast_horizon_days: int = Field(..., json_schema_extra={"example": 7})
    last_observed_price: float = Field(..., description="Most recent historical price observation", json_schema_extra={"example": 1645.0})
    current_price: Optional[float] = Field(None, description="Alias for last_observed_price", json_schema_extra={"example": 1645.0})
    predicted_end_price: float = Field(..., description="Forecasted price at the end of the horizon", json_schema_extra={"example": 1547.54})
    forecasted_end_price: Optional[float] = Field(None, description="Alias for predicted_end_price", json_schema_extra={"example": 1547.54})
    projected_percentage_change: float = Field(..., description="Expected price percentage change over horizon", json_schema_extra={"example": -5.92})
    price_change_percentage: Optional[float] = Field(None, description="Alias for projected_percentage_change", json_schema_extra={"example": -5.92})
    price_change_absolute: Optional[float] = Field(None, description="Absolute change (forecasted - current)", json_schema_extra={"example": -97.46})
    trend_direction: str = Field(..., description="Projected price trajectory (UPWARD, DOWNWARD, STABLE)", json_schema_extra={"example": "DOWNWARD"})
    forecasts: List[PriceForecastDayItem] = Field(..., description="Day-by-day forecasted price sequence")
    execution_time_ms: float = Field(..., description="Inference latency in milliseconds", json_schema_extra={"example": 28.5})
    model_type: str = Field("LSTM", description="Model architecture type", json_schema_extra={"example": "LSTM"})

    def model_post_init(self, __context: Any) -> None:
        if self.current_price is None:
            self.current_price = self.last_observed_price
        if self.forecasted_end_price is None:
            self.forecasted_end_price = self.predicted_end_price
        if self.price_change_percentage is None:
            self.price_change_percentage = self.projected_percentage_change
        if self.price_change_absolute is None:
            self.price_change_absolute = round(self.predicted_end_price - self.last_observed_price, 2)
