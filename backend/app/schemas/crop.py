from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class CropRecommendationRequest(BaseModel):
    """
    Input soil and climatic parameters for crop recommendation.
    """
    N: float = Field(..., ge=0.0, le=200.0, description="Nitrogen ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 35.0})
    P: float = Field(..., ge=0.0, le=200.0, description="Phosphorus ratio in soil (0-200 kg/ha)", json_schema_extra={"example": 70.0})
    K: float = Field(..., ge=0.0, le=250.0, description="Potassium ratio in soil (0-250 kg/ha)", json_schema_extra={"example": 45.0})
    temperature: float = Field(..., ge=0.0, le=60.0, description="Ambient temperature in Celsius (0-60°C)", json_schema_extra={"example": 26.0})
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage (0-100%)", json_schema_extra={"example": 68.0})
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH level (3.0-10.0)", json_schema_extra={"example": 6.7})
    rainfall: float = Field(..., ge=0.0, le=3500.0, description="Annual precipitation / rainfall in mm (0-3500mm)", json_schema_extra={"example": 850.0})
    top_k: int = Field(5, ge=1, le=10, description="Number of ranked crop recommendations to return", json_schema_extra={"example": 5})
    country: Optional[str] = Field("India", description="Optional country context (e.g. India)", json_schema_extra={"example": "India"})
    state: Optional[str] = Field(None, description="Optional State/Province context (e.g. Maharashtra, Punjab)", json_schema_extra={"example": "Maharashtra"})
    district: Optional[str] = Field(None, description="Optional District/Region context (e.g. Nagpur, Amravati)", json_schema_extra={"example": "Nagpur"})
    season: Optional[str] = Field(None, description="Optional agricultural cropping season (Kharif, Rabi, Zaid, Whole Year)", json_schema_extra={"example": "Kharif"})


class CropRecommendationItem(BaseModel):
    """
    Individual ranked crop recommendation with neural network probability and ICAR agronomic suitability index.
    """
    crop: str = Field(..., description="Recommended crop species name", json_schema_extra={"example": "soybean"})
    probability: float = Field(..., ge=0.0, le=1.0, description="Raw neural network softmax probability (0.0 to 1.0)", json_schema_extra={"example": 0.8724})
    model_score: float = Field(..., ge=0.0, le=1.0, description="Raw model confidence score (0.0 to 1.0)", json_schema_extra={"example": 0.8724})
    agronomic_score: float = Field(..., ge=0.0, le=100.0, description="ICAR biophysical agronomic suitability score (0-100)", json_schema_extra={"example": 94.2})
    composite_score: float = Field(..., ge=0.0, le=100.0, description="Weighted composite decision score (0-100)", json_schema_extra={"example": 90.72})
    suitability: str = Field(..., description="Qualitative suitability level (Highly Suitable, Suitable, Moderately Suitable)", json_schema_extra={"example": "Highly Suitable"})
    is_feasible: bool = Field(True, description="Flag indicating if crop meets biophysical feasibility threshold")
    is_perennial: bool = Field(False, description="Flag indicating if crop is a perennial/plantation species requiring extended site validation")
    is_season_compatible: bool = Field(True, description="Flag indicating if crop aligns with current cropping season")
    is_primary: bool = Field(True, description="Flag indicating if crop satisfies primary recommendation criteria")
    recommendation_level: str = Field("PRIMARY", description="Tier level: PRIMARY, SECONDARY, or PRELIMINARY", json_schema_extra={"example": "PRIMARY"})
    quadrant: Optional[str] = Field(None, description="4-Quadrant diagnostic (e.g. Strong ML + Strong Agronomy)", json_schema_extra={"example": "Strong ML + Strong Agronomy"})
    rationale: str = Field(..., description="Agronomic rationale and limiting/optimal factor explanation", json_schema_extra={"example": "Optimal temperature (26.0°C) and rainfall (850 mm) for Soybean."})
    rank: int = Field(1, ge=1, le=20, description="Rank position (1 to 20)", json_schema_extra={"example": 1})


class CropRecommendationResponse(BaseModel):
    """
    Crop Recommendation prediction result payload with Top-K rankings and distribution diagnostics.
    """
    recommended_crop: str = Field(..., description="Top ranked recommended crop", json_schema_extra={"example": "soybean"})
    confidence: float = Field(..., description="Raw model probability of top crop", json_schema_extra={"example": 0.8724})
    suitability: str = Field(..., description="Qualitative suitability level of top crop", json_schema_extra={"example": "Highly Suitable"})
    primary_recommendations: List[CropRecommendationItem] = Field(default_factory=list, description="Primary crop recommendations with strong ML & agronomy support")
    secondary_recommendations: List[CropRecommendationItem] = Field(default_factory=list, description="Secondary or preliminary plausible crops with weak ML or specialty factors")
    recommendations: List[CropRecommendationItem] = Field(..., description="Top ranked crop recommendations (Primary candidates)")
    top_recommendations: List[CropRecommendationItem] = Field(default_factory=list, description="Alias for top ranked recommendations")
    input_parameters: Dict[str, float] = Field(default_factory=dict, description="Echoed input soil and climate parameters")
    execution_time_ms: float = Field(..., description="Inference latency in milliseconds", json_schema_extra={"example": 12.4})
    model_type: str = Field("Bidirectional LSTM (30 classes) + ICAR Agronomic Suitability Engine", description="Underlying neural architecture")
    out_of_distribution: bool = Field(False, description="Flag indicating if inputs deviate from training distribution")
    ood_warnings: List[str] = Field(default_factory=list, description="Informative distribution warnings if any parameter is atypical")
    location_context: Optional[Dict[str, Optional[str]]] = Field(None, description="Contextual location metadata")
