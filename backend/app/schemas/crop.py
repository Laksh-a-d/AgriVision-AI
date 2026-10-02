from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class CropRecommendationRequest(BaseModel):
    """
    Input soil and climatic parameters for crop recommendation.
    """
    N: float = Field(..., ge=0.0, le=200.0, description="Nitrogen ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 90.0})
    P: float = Field(..., ge=0.0, le=200.0, description="Phosphorus ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 42.0})
    K: float = Field(..., ge=0.0, le=250.0, description="Potassium ratio in soil (0-250 kg/ha)", json_schema_extra={"example": 43.0})
    temperature: float = Field(..., ge=0.0, le=60.0, description="Ambient temperature in Celsius (0-60°C)", json_schema_extra={"example": 20.87})
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage (0-100%)", json_schema_extra={"example": 82.00})
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH level (3.0-10.0)", json_schema_extra={"example": 6.50})
    rainfall: float = Field(..., ge=0.0, le=500.0, description="Precipitation / rainfall in mm (0-500mm)", json_schema_extra={"example": 202.93})
    top_k: int = Field(5, ge=1, le=10, description="Number of ranked crop recommendations to return", json_schema_extra={"example": 5})
    country: Optional[str] = Field("India", description="Optional country context (e.g. India)", json_schema_extra={"example": "India"})
    state: Optional[str] = Field(None, description="Optional State/Province context (e.g. Maharashtra, Punjab)", json_schema_extra={"example": "Maharashtra"})
    district: Optional[str] = Field(None, description="Optional District/Region context (e.g. Nagpur, Amravati)", json_schema_extra={"example": "Nagpur"})


class CropRecommendationItem(BaseModel):
    """
    Individual ranked crop recommendation with confidence probability and rank index.
    """
    crop: str = Field(..., description="Recommended crop species name", json_schema_extra={"example": "rice"})
    probability: float = Field(..., ge=0.0, le=1.0, description="Confidence probability (0.0 to 1.0)", json_schema_extra={"example": 0.9412})
    rank: int = Field(1, ge=1, le=10, description="Rank position (1 to 10)", json_schema_extra={"example": 1})


class CropRecommendationResponse(BaseModel):
    """
    Crop Recommendation prediction result payload with Top-K rankings and distribution diagnostics.
    """
    recommended_crop: str = Field(..., description="Top ranked recommended crop", json_schema_extra={"example": "rice"})
    confidence: float = Field(..., description="Confidence probability of top crop", json_schema_extra={"example": 0.9412})
    recommendations: List[CropRecommendationItem] = Field(..., description="Top-K ranked crop recommendations")
    top_recommendations: List[CropRecommendationItem] = Field(default_factory=list, description="Alias for top-K ranked recommendations")
    input_parameters: Dict[str, float] = Field(default_factory=dict, description="Echoed input soil and climate parameters")
    execution_time_ms: float = Field(..., description="Inference latency in milliseconds", json_schema_extra={"example": 12.4})
    model_type: str = Field("Bidirectional LSTM (22 classes)", description="Underlying neural architecture")
    out_of_distribution: bool = Field(False, description="Flag indicating if inputs deviate from training distribution")
    ood_warnings: List[str] = Field(default_factory=list, description="Informative distribution warnings if any parameter is atypical")
    location_context: Optional[Dict[str, Optional[str]]] = Field(None, description="Contextual location metadata")
